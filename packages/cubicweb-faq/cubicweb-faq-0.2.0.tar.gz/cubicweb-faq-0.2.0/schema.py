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

"""cubicweb-faq schema"""

from yams.buildobjs import (String, RichString, EntityType,
                            SubjectRelation)

class FAQSection(EntityType):
    title = String(unique=True, required=True, fulltextindexed=True,
                   maxsize=256)


class FAQuestion(EntityType):
    question = String(maxsize=256, required=True, fulltextindexed=True)
    answer = RichString(fulltextindexed=True)
    in_faq_section = SubjectRelation('FAQSection', cardinality='1*', inlined=True,
                                     composite='object')
