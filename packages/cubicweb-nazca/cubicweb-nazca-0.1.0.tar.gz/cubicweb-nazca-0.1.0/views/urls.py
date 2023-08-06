# copyright 2013-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr

"""cubicweb-nazca url rewrite rules"""

import re

from cubicweb.web.views.urlrewrite import SimpleReqRewriter

class NazcaRewriter(SimpleReqRewriter):
    rules = [('/nazca', {'vid': r'nazca'}),
             (re.compile('/nazca-(.*)$'), {'vid': r'nazca-\1'}),]
