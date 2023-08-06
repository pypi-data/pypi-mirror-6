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

"""cubicweb-faq views/forms/actions/components for web ui"""


from cubicweb.predicates import is_instance
from cubicweb.web.views import primary, baseviews, uicfg


class FAQSectionViewMixin(object):

    def render_questions(self, section):
        questions_rset = section.related('in_faq_section', 'object')
        if questions_rset:
            self.wview('list', questions_rset)
        else:
            self.w(u'<div class="searchMessage"><strong>%s</strong></div>\n'
                   % _('This FAQ section has no question.'))


class FAQSectionListItemView(FAQSectionViewMixin, baseviews.SameETypeListItemView):
    __select__ = (baseviews.SameETypeListItemView.__select__ &
                  is_instance("FAQSection"))

    def cell_call(self, row, col, **kwargs):
        section = self.cw_rset.get_entity(row, col)
        self.w(u'<h4><a href="%s">%s</a></h4>' %
               (section.absolute_url(), section.printable_value('title')))
        self.render_questions(section)


class FAQSectionPrimaryView(FAQSectionViewMixin, primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('FAQSection')

    def render_entity_attributes(self, entity):
        self.render_questions(entity)


class FAQuestionPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('FAQuestion')
    show_attr_label = False

    def render_entity_attributes(self, entity):
        if not entity.answer:
            self.w(u'<div class="searchMessage"><strong>%s</strong></div>\n'
                   % _('This question has not been answered yet.'))
        else:
            super(FAQuestionPrimaryView, self).render_entity_attributes(entity)


# uicfg
_pvs = uicfg.primaryview_section
_dispctrl = uicfg.primaryview_display_ctrl

# FAQSection
_pvs.tag_object_of(('FAQuestion', 'in_faq_section', 'FAQSection'), 'hidden')

# FAQuestion
_pvs.tag_attribute(('FAQuestion', 'question'), 'hidden')
_pvs.tag_subject_of(('FAQuestion', 'in_faq_section', 'FAQSection'), 'hidden')
_dispctrl.tag_subject_of(('FAQuestion', 'in_faq_section', 'FAQSection'), {'vid': 'reledit'})
