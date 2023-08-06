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

"""cubicweb-brainomics entity's classes"""
import os.path as osp

from cubes.medicalexp.entities import compute_fullfilepath
from cubes.neuroimaging.entities import Scan
from cubes.genomics.entities import GenomicMeasure

MEASURES = ['GenericMeasure', 'Scan', 'GenericTestRun', 'QuestionnaireRun', 'GenomicMeasure']


class BrainomicsScan(Scan):

    @property
    def full_filepath(self):
        return compute_fullfilepath(self)


class BrainomicsGenomicMeasure(GenomicMeasure):

    @property
    def full_filepath(self):
        return compute_fullfilepath(self)


##############################################################################
from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance

class AssessmentICalendarableAdapter(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = EntityAdapter.__select__ & is_instance('Assessment')

    @property
    def start(self):
        return self.entity.datetime

    @property
    def end(self):
        return self.entity.datetime
