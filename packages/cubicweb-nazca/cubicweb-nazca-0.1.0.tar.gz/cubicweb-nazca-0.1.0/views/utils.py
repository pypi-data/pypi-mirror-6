# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""cubicweb-nazca utils for web ui"""

import re
from collections import defaultdict

from logilab.common import flatten

from nazca.rl.aligner import BaseAligner, PipelineAligner
from nazca.rl.blocking import NGramBlocking, KdTreeBlocking, \
                MinHashingBlocking, KmeansBlocking
from nazca.utils.dataio import sparqlquery, rqlquery, parsefile
from nazca.utils.distances import LevenshteinProcessing, \
     GeographicalProcessing, BaseProcessing, SoundexProcessing
from nazca.utils.normalize import BaseNormalizer, UnicodeNormalizer, \
                                   SimplifyNormalizer, NormalizerPipeline

DISTANCES_OBJECTS = {_(''): None,
             _('Levenshtein'): LevenshteinProcessing,
             _('Geographical'): GeographicalProcessing,
             _('Soundex'): SoundexProcessing,
             _('Euclidean'): BaseProcessing,
            }

NORMALIZERS_OBJECTS = {_(''): [],
                       _('Simplify'): SimplifyNormalizer,
                       _('Unicode'): UnicodeNormalizer,
                       _('Base'):BaseNormalizer,
                       }

BLOCKINGS_OBJECTS =  {
               _('NGram'): NGramBlocking,
                _('Kdtree'): KdTreeBlocking,
                _('Minhashing'): MinHashingBlocking,
                _('Kmeans'): KmeansBlocking,
              }

OUTPUTS = ('csv', 'html', 'json') #, 'rdf')

###############################################################################
### UTILITY FUNCTIONS #########################################################
###############################################################################
def parseindexes(indexesstr):
    """ Read indexsstr and return a python list
        >>> parseindexes('1, 2, (3, 5), (3, 4)')
        (1, 2, (3, 5), (3, 4))
        >>> parseindexes('A, B, CD, (E, F), (G, (H, I, J), K)')
        ('A', 'B', 'CD', ('E', 'F'), ('G', ('H', 'I', 'J)', 'K'))
    """
    indexes = []
    if not indexesstr:
        return indexes
    openers = '(['
    closers = ')]'
    stack = []
    it = iter(indexesstr.split(','))
    for index in it:
        index = index.strip()
        if index[0] in openers:
            stack.append(index[0])
            try:
                while len(stack):
                    follower = it.next().strip()
                    index += ',' + follower
                    if follower[-1] in closers:
                        stack.pop()
                    elif follower[0] in openers:
                        stack.append(index[-1])
            except StopIteration:
                raise ValueError('bad formatted string')
            indexes.append(parseindexes(index[1:-1]))
        elif index.isdigit():
            indexes.append(int(index))
        else:
            indexes.append(index)
    return tuple(indexes)

def getvars(query, _type):
    """ Get the variables """
    if _type not in set(['rql', 'sparql']):
        raise NotImplementedError()
    if _type == 'rql':
        regex = '(?:any)(.*)(?:group|order|limit|where)'
    elif _type == 'sparql':
        regex = '(?:select(?: ?distinct)?)(.*)(?:where)'
    # Build regexp
    query = re.sub('(\r\n|\n|\r)', ' ', query)
    allvars = re.search(regex, query.lower())
    return tuple([v.strip() for v in allvars.group(1).split(',')])

def getindexesfromvars(indexes, query, _type):
    """ Get the indexes from variables """
    allvars = getvars(query, _type)
    indexes = indexes.lower()
    for pos, var in enumerate(allvars):
        var = var.replace('?', r'\?')
        indexes = re.sub(r'%s([^\w]|$)' % var, r'%s\1' % str(pos), indexes)
    return parseindexes(indexes)

###############################################################################
### BUILDING FUNCTIONS ########################################################
###############################################################################
def stringlist(value):
    return [i.strip() for i in value.split(',')]

def intlist(value):
    return [int(i.strip()) for i in value.split(',')]

CASTFUNC = {'float': float, 'int':int, 'bool': bool,
            'stringlist': stringlist,
            'intlist':intlist}


def alignall(refset, targetset, processings, threshold,
             blockings=None,
             ref_normalizations=None,
             target_normalizations=None):
    aligners = []
    # Aligner
    aligner = BaseAligner(threshold=threshold, processings=processings)
    if ref_normalizations:
        # katia : can we have several normalizer for an index?
        # Is there an order?
        for normalizer in ref_normalizations:
            aligner.register_ref_normalizer(normalizer)
    if target_normalizations:
        # katia : can we have several normalizer for an index?
        for normalizer in ref_normalizations:
            aligner.register_target_normalizer(normalizer)
    # use PipelineBlocking ? wich order ?
    for blocking in blockings:
        aligner.register_blocking(blocking)
    pairs = []
    for pair in aligner.get_aligned_pairs(refset, targetset):
        pairs.append(pair)
    return pairs

def build_distances_from_form(session):
    """ Build the distances from a form """
    params = build_params_from_form(session, '__distance')
    distances = []
    for index, options in params.iteritems():
        funcname = DISTANCES_OBJECTS[options.pop('_funcname')]
        # the user will use not python, but humain indexes
        options['ref_attr_index'] = options.pop('source')
        options['target_attr_index'] = options.pop('target')
        distances.append(funcname(**options))
    return distances

def build_blockings_from_form(session):
    """ Build the blockings from a form """
    params = build_params_from_form(session, '__neighbours')
    blockings = []
    for index, options in params.iteritems():
        funcname = BLOCKINGS_OBJECTS[options.pop('_funcname')]
        source = options.pop('source')
        target = options.pop('target')
        blockings.append(funcname(source, target, **options))
    return blockings

def build_normalizations_from_form(session):
    """ Build the normalizations from a form """
    params = build_params_from_form(session, '__normalize')
    ref_normalizations = []
    target_normalizations = []
    for index, options in params.iteritems():
        funcname = NORMALIZERS_OBJECTS[options.pop('_funcname')]
        source_indexes = options.pop('source')
        target_indexes = options.pop('target')
        for idx in options.pop('source'):
            ref_normalizations.append(funcname(attr_index=idx+1, **options))
        for idx in options.pop('target'):
            target_normalizations.append(funcname(attr_index=idx+1, **options))
    return ref_normalizations, target_normalizations

def build_params_from_form(session, name):
    """ Build the blockings from a form :
    name are : __neighbours_1

    """
    form = session.form
    params = defaultdict(dict)
    regex = '%s_(?P<index>\d)_(?P<option>.*)' % name
    objects = []
    for key, value in form.iteritems():
        res = re.search(regex, key)
        if res:
            name = res.group('option')
            try:
                name, castfunc = name.split(':')
                value = CASTFUNC[castfunc](value)
            except ValueError:
                pass
            params[res.group('index')].update({name:value})
    return params

def build_threshold_from_form(session):
    return float(session.form['__threshold'])

def build_distances_from_entity(session):
    raise NotImplementedError()

def build_blockings_from_entity(session):
    raise NotImplementedError()

def build_normalizations_from_entity(session, entity):
    """ Build the treatements from an entity"""
    raise NotImplementedError()

def build_threshold_from_entity(session):
    raise NotImplementedError()

def build_alignset_from_form(session, messages, aligntype):
    """ Build the alignset from a form """
    _ = session._
    form = session.form
    align_dict = {}
    if form.get('__%stype' % aligntype) == 'csv':
        messages.append(_('Reading the %s file' % aligntype))
        alignset = parsefile(session.session.data['__%sfile' % aligntype],
                             indexes=parseindexes(form['__%sindexes' % aligntype]),
                             use_autocast=False)
    else:
        kwargs = {}
        if form.get('__%stype' % aligntype) == 'sparql':
            querier = sparqlquery
            kwargs['raise_on_error'] = True
            indexes = getindexesfromvars(form['__%sindexes' % aligntype],
                                         form['__%sreq' % aligntype],
                                         'sparql')
        elif form.get('__%stype' % aligntype) == 'rql':
            querier = rqlquery
            indexes = getindexesfromvars(form['__%sindexes' % aligntype],
                                         form['__%sreq' % aligntype],
                                         'rql')
        kwargs['indexes'] = indexes
        if aligntype == 'align':
            messages.append(_('Running the align query'))
        else:
            messages.append(_('Running the target query'))
        alignset = querier(form.get('__%ssource' % aligntype), form.get('__%sreq' % aligntype),
                           **kwargs)
        align_dict = {'%sset_request' % aligntype: form.get('__%sreq' % aligntype),
                      '%sset_type' % aligntype: form.get('__%stype' % aligntype),
                      '%sset_source' % aligntype: form.get('__%ssource' % aligntype),
                      '%sset_indexes' % aligntype: form['__%sindexes' % aligntype]}
    return alignset, align_dict

def build_alignset_from_entity(session, messages, entity):
    """ Build the alignset from an entity """
    # Alignset
    _ = session._
    if entity.alignset_type == 'csv':
        messages.append(_('Reading the align file'))
        alignset = parsefile(session.session.data['__alignfile'],
                             indexes=parseindexes(entity.alignset_indexes),
                             use_autocast=False)
    else:
        if entity.alignset_type == 'sparql':
            querier = sparqlquery
            indexes = getindexesfromvars(entity.alignset_indexes,
                                         entity.alignset_request,
                                         'sparql')
        elif entity.alignset_type == 'rql':
            querier = rqlquery
            indexes = getindexesfromvars(entity.alignset_indexes,
                                         entity.alignset_request,
                                         'rql')
        messages.append(_('Running the align query'))
        alignset = querier(entity.alignset_source, entity.alignset_request, indexes=indexes)
    # Targetset
    if entity.targetset_type == 'csv':
        messages.append(_('Reading the target file'))
        targetset = parsefile(session.session.data['__targetfile'],
                              indexes=parseindexes(entity.targetset_indexes),
                              use_autocast=False)
    else:
        if entity.targetset_type == 'sparql':
            querier = sparqlquery
            indexes = getindexesfromvars(entity.targetset_indexes,
                                         entity.targetset_request,
                                         'sparql')
        elif entity.targetset_type == 'rql':
            querier = rqlquery
            indexes = getindexesfromvars(entity.targetset_indexes,
                                         entity.targetset_request,
                                         'rql')
        messages.append(_('Running the target query'))
        targetset = querier(entity.targetset_source, entity.targetset_request, indexes=indexes)
    return alignset, targetset

def run_nazca(session, entity=None):
    """ Run the Nazca alignment function"""
    _ = session._
    form = session.form
    session.session.data['messages'] = []
    messages = session.session.data['messages']
    try:
        if not entity:
            # Blocking
            blockings = build_blockings_from_form(session)
            # Distances
            distances = build_distances_from_form(session)
            # Normalizations
            ref_normalizations, target_normalizations = build_normalizations_from_form(session)
            # #threshold
            threshold = build_threshold_from_form(session)

        else:
            # Blocking
            blockings = build_blockings_from_entity(session, entity)
            # Distances
            distances = build_distances_from_entity(session, entity)
            # Normalizations
            ref_normalizations, target_normalizations = build_normalizations_from_entity(session, entity)
            # #threshold
            threshold = build_threshold_from_entity(session)
        if not distances:
            raise ValueError(_('You specified no distance function to apply'))
        targetset = ()
        refset = ()
        align_dict = {}
        # Refset and TargetSet
        if entity is None:
            # Refset
            refset, refset_dict = build_alignset_from_form(session, messages, 'align')
            align_dict.update(refset_dict)
            # Targetset
            targetset, targetset_dict = build_alignset_from_form(session, messages, 'target')
            align_dict.update(targetset_dict)
        else:
            refset, targetset = build_refset_from_entity(session, messages, entity)
        messages.append(_('Starting the alignment'))
        results = alignall(refset, targetset, distances, threshold,
                           blockings=blockings,
                           ref_normalizations=ref_normalizations,
                           target_normalizations=target_normalizations)
        # do not change the id message as it is used to check the resluts
        # in javascrtip `checkProgress`
        messages.append(_('results_done'))
        list_results = []
        for line in results:
            list_results.append(flatten(line))
        session.info('cubes.nazca.utils.run_nacza: %s results' % len(list_results))
        session.session.data['results'] = list_results
    except Exception, err:
        messages.append(_('An error occured <strong>%s</strong>')
                        % err)
        messages.append(_('results_aborded'))
