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
from collections import defaultdict
from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView
from cubicweb.web.views.baseviews import ListView


###############################################################################
### LIST VIEW #################################################################
###############################################################################
class BrainomicsListView(ListView):

    def call(self, klass=None, title=None, subvid=None, listid=None, **kwargs):
        super(BrainomicsListView, self).call(klass="unstyled stripped",
                                             title=title, subvid=subvid,
                                             listid=listid, **kwargs)


###############################################################################
### CARD VIEW #################################################################
###############################################################################
class BrainomicsCardDocumentation(EntityView):
    __regid__ = 'documentation_card'
    __select__ = EntityView.__select__ & is_instance('Card')

    def call(self, rset=None, **kwargs):
        rset = rset or self.cw_rset
        w = self.w
        w(u'<div>')
        for entity in rset.entities():
            w(u'<h2>%s</h2>' % xml_escape(entity.title))
            if entity.synopsis:
                w(u'<blockquote><p>%s</p></blockquote>' % xml_escape(entity.synopsis))
            if entity.content:
                w(entity.content)
        w(u'</div>')


###############################################################################
### RESOURCES VIEW ############################################################
###############################################################################
class BrainomicsResultFile(EntityView):
    __regid__ = 'results-view'
    __select__ = EntityView.__select__ & is_instance('Questionnaire', 'QuestionnaireRun',
                                                     'GenomicMeasure', 'Scan')

    def entity_call(self, entity):
        # Display results file
        w = self.w
        rset = self._cw.execute('Any F WHERE X results_file F, X eid %(e)s',
                                {'e': entity.eid})
        if rset:
            w(u'<h3>%s</h3>' % self._cw._('Results file'))
            self.wview('list', rset=rset)


###############################################################################
### AGGREGATED VIEW ###########################################################
###############################################################################
class BrainomicsAggregatedView(EntityView):
    __regid__ = 'aggregated-view'

    def call(self, rset=None):
        rset = rset or self.cw_rset
        row_types = list(set(row[0] for row in rset.description))
        if len(row_types) > 1 or not row_types:
            raise RQLException('Wrong result set query: %s' % rset.rql)
        row_type = row_types[0]
        table = defaultdict(dict)
        for row in rset:
            table.setdefault(row[0], {})
            table[row[0]].update({row[1]: row[2]})
        return self._html_table_from_data(table, row_type)

    def _html_table_from_data(self, table_data, row_type):
        """Build html table out of a Python dictionary with eids and values.

           `table_data` is a dictionary with one key for each table row.
           The value of each such key is a dictionary, with one key for each column.
           The value of such a key is the value one wishes to put in the table cell.

           `row_type` is a string holding the yams entity type of the entities
           which occupy the first cell on each row.
        """
        # header first
        self.w(u'<table><tr><th>%s</th>' % xml_escape(self._cw._(row_type)))
        # Empty td first to leave room for first column
        header_content = ''.join(u'<th><a href="%s">%s</a></th>'
                                 % (ent.absolute_url(), ent.dc_title())
                                 for ent in map(self._cw.entity_from_eid,
                                                set(kcol for krow in table_data
                                                    for kcol in table_data[krow])))
        self.w(header_content)
        self.w(u'</tr>')
        # now the rows
        for row in table_data:
            self.w(u'<tr>')
            # first row element:
            row_ent = self._cw.entity_from_eid(row)
            self.w(u'<td align="center"><a href="%s">%s</td>'
                   % (row_ent.absolute_url(), row_ent.dc_title()))
            row_content = ''.join(u'<td align="center">%s</td>'
                                  % table_data[row][col]
                                  for col in table_data[row])
            self.w(row_content)
            self.w(u'</tr>')
        self.w(u'</table>')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (BrainomicsListView,))
    vreg.register_and_replace(BrainomicsListView, ListView)
