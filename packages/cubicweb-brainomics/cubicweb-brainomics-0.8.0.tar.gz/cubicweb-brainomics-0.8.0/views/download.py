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

import os
import os.path as osp
import tempfile
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


CSV_DOWNLOADABLE = ('Subject', 'Scan', 'ScoreDefinition', 'QuestionnaireRun',
                    'Answer', 'GenomicMeasure', 'Snp', 'GenericTestRun')
XCEDE_DOWNLOADABLE = ('Subject', 'Scan', 'GenomicMeasure', 'QuestionnaireRun', 'Questionnaire')
JSON_DOWNLOADABLE = ('Subject',)
ZIP_DOWNLOADABLE = ('Scan', 'GenomicMeasure')
ALL_DOWNLOADABLE = set(CSV_DOWNLOADABLE + XCEDE_DOWNLOADABLE + ZIP_DOWNLOADABLE)


###############################################################################
### UTILITY FUNCTIONS #########################################################
###############################################################################
def zipfiles(filepaths):
    """generates a zip archive from `filepaths`

    :param filepaths: is a dictionary mapping basename (as it will appear in the
                      archive) to corresponding absolute filepath (where it must
                      read from on the filesystem)

    :return: a couple fileobj, filepath where `fileobj` is a standard python
             open file objet on the generated archive, and `filepath` is an
             absolute file path to this archive on the filesystem
    """
    fd, archive_filepath = tempfile.mkstemp()
    try:
        noext_archivename = osp.splitext(DataZipView.archive_name)[0]
        with closing(ZipFile(archive_filepath, "w", ZIP_DEFLATED, True)) as zip:
            for filename, subj, filepath in filepaths:
                zip.write(filepath, '%s/%s/%s' % (noext_archivename, subj, filename))
        fileobj = os.fdopen(fd)
        fileobj.seek(0)
        return fileobj, archive_filepath
    except:
        os.close(fd)
        os.unlink(archive_filepath)
        raise


###############################################################################
### ZIP VIEWS #################################################################
###############################################################################
class DataZipView(EntityView):
    """Abstract base class for the zip view"""
    __regid__ = 'data-zip'
    __select__ = EntityView.__select__ & is_instance(*ZIP_DOWNLOADABLE)
    templatable = False
    binary = True
    archive_name = 'brainomics_data.zip'

    def set_request_content_type(self):
        self._cw.set_content_type('application/zip', filename=self.archive_name)

    def call(self):
        if not self.cw_rset:
            return
        filepaths = set()
        for entity in self.cw_rset.entities():
            if entity.__regid__ == 'GenomicMeasure':
                for ext in ('.bim', '.bed', '.fam'):
                    filepath = osp.splitext(osp.basename(entity.filepath))[0] + ext
                    full_filepath = osp.splitext(entity.full_filepath)[0] + ext
                    filepaths.add((filepath, entity.concerns[0].identifier, full_filepath))
            else:
                filename = entity.type + '_' + osp.basename(entity.filepath)
                filename = filename.replace(' ', '_')
                filepaths.add((filename, entity.concerns[0].identifier, entity.full_filepath))
            for external_resource in entity.external_resources:
                filepaths.add((osp.basename(external_resource.filepath),
                               entity.concerns[0].identifier,
                               external_resource.full_filepath))
        fileobj, archive_filepath = zipfiles(list(filepaths))
        try:
            self.w(fileobj.read())
        finally:
            fileobj.close()
            os.unlink(archive_filepath)
