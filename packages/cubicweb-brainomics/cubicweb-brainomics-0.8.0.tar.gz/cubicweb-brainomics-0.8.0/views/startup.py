# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
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

"""cubicweb-brainomics views/forms/actions/components for web ui"""

from cubicweb.web.views.startup import IndexView


class BrainomicsIndexView(IndexView):

    def call(self, **kwargs):
        self.w(u'<div class="col-md-12">')
        self.w(u'<div class="row">')
        url = self._cw.data_url('images/subject.png')
        href = self._cw.build_url(rql='Any X WHERE X is Subject')
        self.w(u'<div class="col-md-3"><h2>Subjects</h2><a href="%s"><img width="200" src="%s"/></a></div>'
               % (href, url))
        url = self._cw.data_url('images/images.png')
        href = self._cw.build_url(rql=('Any X, XT, XL, XI, XF, XD WHERE X is Scan, '
                                       'X type XT, X label XL, X identifier XI, '
                                       'X format XF, X description XD'))
        self.w(u'<div class="col-md-3"><h2>Images</h2><a href="%s"><img width="200" src="%s"/></a></div>'
               % (href, url))
        url = self._cw.data_url('images/genetics.png')
        href = self._cw.build_url(vid='list', rql='(Any X WHERE X is GenomicMeasure) '
                                  'UNION (Any X WHERE X is GenericTestRun, X instance_of T, T type "genomics")')
        self.w(u'<div class="col-md-3"><h2>Genetics</h2><a href="%s"><img width="200" src="%s"/></a></div>'
               % (href, url))
        url = self._cw.data_url('images/questionnaire.png')
        href = self._cw.build_url(rql='Any X, XI, XD WHERE X is QuestionnaireRun, X identifier XI, X datetime XD')
        self.w(u'<div class="col-md-3"><h2>Questionnaires</h2><a href="%s"><img width="200" src="%s"/></a></div>'
               % (href, url))
        self.w(u'</div>')
        self.w(u'</div>')
        self.w(u'</div>')
        self.w(u'<div class="col-md-12">')
        self.w(u'<div class="row">')
        for title in ('index', 'rqlexamples'):
            card = self._cw.execute('Any X WHERE X is Card, X title %(t)s', {'t': title})
            if card:
                self.w(card.get_entity(0,0).content)
        self.w(u'</div>')
        self.w(u'</div>')


def registration_callback(vreg):
    vreg.register_and_replace(BrainomicsIndexView, IndexView)
