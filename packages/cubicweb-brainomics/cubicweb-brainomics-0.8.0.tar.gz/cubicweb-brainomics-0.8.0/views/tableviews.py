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
from logilab.mtconverter import xml_escape
from cubicweb.selectors import is_instance
from cubicweb.web.views.tableview import (TableLayout, EntityTableView,
                                          RelationColRenderer, EntityTableColRenderer)


###############################################################################
### TABLE LAYOUT ##############################################################
###############################################################################
class FilterTableLayout(TableLayout):
    __regid__ = 'filter_table_layout'
    display_filter = 'top'
    hide_filter = False


###############################################################################
### GENOMIC MEASURE - CGH #####################################################
###############################################################################
class AbstractCghTableView(EntityTableView):
    __abtract__ = True
    layout_id = 'filter_table_layout'
    paginable = False
    __select__ = EntityTableView.__select__ & is_instance('CghResult')


class CghTableView(AbstractCghTableView):
    __regid__ = 'genmeas-table-view'
    columns = ['genomic_region', 'cgh_ratio', 'log2_ratio', 'status', 'numprobes']
    column_renderers = {'genomic_region': RelationColRenderer(role='subject')}


class GeneCghTableView(AbstractCghTableView):
    __regid__ = 'gene-genmeas-table-view'
    columns = ['genomic_region', 'related_measure', 'cgh_ratio', 'log2_ratio', 'status']
    column_renderers = {'related_measure': RelationColRenderer(role='subject', vid='incontext'),
                        'genomic_region': RelationColRenderer(role='subject', vid='incontext')}


class RegionCghTableView(EntityTableView):
    __regid__ = 'region-genmeas-table-view'
    columns = ['related_measure', 'cgh_ratio', 'log2_ratio', 'status']
    column_renderers = {'related_measure': RelationColRenderer(role='subject', vid='incontext')}


###############################################################################
### GENOMIC MEASURE - SEQUENCAGE ##############################################
###############################################################################
class AbstractMutationTableView(EntityTableView):
    __abstract__ = True
    layout_id = 'filter_table_layout'
    paginable = False
    __select__ = EntityTableView.__select__ & is_instance('Mutation')

    columns = ['valid', 'mutation_id', 'mutation_type', 'ploidy',
               'reference_base', 'variant_base', 'variant_frequency', 'p_value',
               'coverage', 'reference_coverage', 'variant_coverage',
               'hotspot_id', 'reference_id', 'comment',
               'protein', 'biological_classification', 'classification_type',
               'locus_version', 'nucl', 'polyphen', 'sift', 'gvd_alignment',
               'base', 'conclusions', 'medical_coverage']


class MutationTableView(AbstractMutationTableView):
    __regid__ = 'genmeas-table-view'

    column_renderers = {'related_gene': RelationColRenderer(role='subject')}

    columns = ['related_gene',] + AbstractMutationTableView.columns


class GeneMutationTableView(AbstractMutationTableView):
    __regid__ = 'gene-genmeas-table-view'

    column_renderers = {'related_measure': RelationColRenderer(role='subject', vid='incontext')}

    columns = ['related_measure',] + AbstractMutationTableView.columns


###############################################################################
### SCORE GROUP ###############################################################
###############################################################################
class ScoreValueOutofContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('ScoreValue')
    __regid__ = 'scorevalue-outofcontext-table-view'

    columns = ['definition', 'text', 'value']
    column_renderers = {'definition': RelationColRenderer(role='subject')}


class ScoreValueInContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('ScoreValue')
    __regid__ = 'scorevalue-incontext-table-view'

    def render_value(w, entity):
        w(u'<ul>%s</ul>' % entity.complete_value)

    def render_datetime(w, entity):
        w(u'<ul>%s</ul>' % (entity.datetime or u'-'))

    def render_target(w, entity):
        if entity.reverse_related_infos:
            w(u'<ul>%s</ul>' % ''.join(u'<li>%s</li>' % e.view('incontext') for
                                       e in entity.reverse_related_infos))
        elif entity.measure:
            w(u'<ul>%s</ul>' % ''.join(u'<li>%s</li>' % m.concerns[0].view('incontext')
                                       for m in entity.measure))

    columns = ['subject', 'value', 'datetime']
    column_renderers = {'datetime': EntityTableColRenderer(renderfunc=render_datetime),
                        'subject': EntityTableColRenderer(renderfunc=render_target),
                        'value': EntityTableColRenderer(renderfunc=render_value)}


###############################################################################
### DRUG TAKES ################################################################
###############################################################################
class DrugTakeTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('DrugTake')
    __regid__ = 'drugtake-table-view'

    columns = ['drug', 'taken_in_therapy', 'start_taking_date', 'stop_taking_date',
               'take_order', 'dosis', 'unit', 'number_of_cycles', 'dosis_percentage',
               'reduced_dosis']
    column_renderers = {'taken_in_therapy': RelationColRenderer(role='subject', vid='incontext'),
                        'drug': RelationColRenderer(role='subject')}


###############################################################################
### ANSWERS ###################################################################
###############################################################################
class AnswerInContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Answer')
    __regid__ = 'answer-incontext-table-view'
    columns = ['answer', 'value', 'datetime']

    def render_value(w, entity):
        w(u'%s' % entity.computed_value)

    def render_text(w, entity):
        w(u'%s' % entity.question[0].text)

    def render_answer(w, entity):
        w(u'<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                    xml_escape(entity.dc_title())))

    column_renderers = {'answer': EntityTableColRenderer(renderfunc=render_answer),
                        'value': EntityTableColRenderer(renderfunc=render_value)}


class AnswerOutOfContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Answer')
    __regid__ = 'answer-outofcontext-table-view'
    columns = ['question', 'text', 'value', 'datetime']

    def render_text(w, entity):
        w(u'%s' % entity.question[0].text)

    def render_question(w, entity):
        entity = entity.question[0]
        w(u'<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                    xml_escape(entity.dc_title())))

    column_renderers = {'question': EntityTableColRenderer(renderfunc=render_question),
                        'text': EntityTableColRenderer(renderfunc=render_text)}


###############################################################################
### QUESTIONS #################################################################
###############################################################################
class QuestionTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Question')
    __regid__ = 'question-table-view'
    columns = ['question', 'text', 'type', 'possible_answers', 'answers']

    def render_question(w, entity):
        w(u'%s'% xml_escape(entity.dc_title()))

    def render_answers(w, entity):
        w(u'<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                    _('See detailed question')))
    
    column_renderers = {'question': EntityTableColRenderer(renderfunc=render_question),
                        'answers': EntityTableColRenderer(renderfunc=render_answers)}
