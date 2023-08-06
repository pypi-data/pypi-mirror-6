# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-nazca schema"""

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, Int, BigInt, Float, Date)



class NazcaAlignment(EntityType):
    name = String()
    alignset_request = String(required=True)
    alignset_type = String(required=True, vocabulary=('rql', 'sparql', 'csv file'))
    alignset_source = String(required=True)
    alignset_indexes = String(required=True)
    # XXX Split in two different source entities ?
    targetset_request = String(required=True)
    targetset_type = String(required=True, vocabulary=('rql', 'sparql', 'csv file'))
    targetset_source = String(required=True)
    targetset_indexes = String()
    neighbouring_method = String()
    neighbouring_indexes = Int()
    neighbouring_th = Float()
    align_threshold = Float(required=True)
    align_keepall = Boolean()


class AlignmentParameter(EntityType):
    normalization = String(required=True)
    distance_function = String(required=True)
    weighting = Float()
    position = Int()


class alignment_parameters(RelationDefinition):
    subject = 'NazcaAlignment'
    object = 'AlignmentParameter'
    cardinality = '**'
