# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-ner schema"""
from yams.buildobjs import EntityType, SubjectRelation, String, Float


###############################################################################
### NER SOURCE ################################################################
###############################################################################
class NerSource(EntityType):
    name = String(maxsize=512, indexed=True)


###############################################################################
### NER ENTRY #################################################################
###############################################################################
class NerEntry(EntityType):
    # uri == cwuri
    label = String(indexed=True, fulltextindexed=True)
    unormalize_label = String(indexed=True, fulltextindexed=True)
    weight = Float(indexed=True)
    lang = String(maxsize=32, indexed=True)
    ner_source = SubjectRelation('NerSource', cardinality='1*', inlined=True)


###############################################################################
### NER PROCESS ###############################################################
###############################################################################
class NerProcess(EntityType):
    name = String(maxsize=512, indexed=True)
    host = String(maxsize=512, indexed=True)
    request = String()
    type = String(maxsize=512, indexed=True)
    lang = String(maxsize=32, indexed=True)
