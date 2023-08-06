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

from cubicweb.web import formfields as ff, Redirect
import cubicweb.web.formwidgets as fwdgs
from cubicweb.view import StartupView
from cubicweb.web.views.basecontrollers import ViewController
from cubicweb.web.views import forms

BROWSABLE_ENTITIES = ('Subject', 'Scan')

class BrainomicsDisplaySpecificEntities(StartupView):
    __regid__ = 'display-specific-entities'

    def call(self):
        self.w(u'<div class="col-md-12">')
        self.w(u'<h2>Display specific entities</h2>')
        self.w(u'<legend>%s</legend>' % self._cw._('Browse for identifiers file'))
        entities_form = self._cw.vreg['forms'].select('browse-identifiers-form', self._cw)
        entities_form.render(w=self.w)
        self.w(u'</div>')


class BrainomicsDisplaySpecificEntitiesForm(forms.FieldsForm):
    __regid__ = 'browse-identifiers-form'
    form_buttons = [fwdgs.SubmitButton(label=_('Validate'), attrs={"class": "btn btn-primary"})]


    @property
    def action(self):
        return self._cw.build_url('browse-identifiers-controller')

    filename = ff.FileField(name='__file',
                            label=_('Indentifiers file to import'),
                            order=1,)

    etype = ff.StringField(name='__etype',
                           label=_('Entity type'),
                           required=True,
                           help=_('Entity type'),
                           order = 2,
                           choices = BROWSABLE_ENTITIES)


class BrainomicsDisplaySpecificEntitiesController(ViewController):
    __regid__ = 'browse-identifiers-controller'

    def _read_uuid_file(self, filename):
        try:
            fdesc = filename[1]
        except IOError as ioerr:
            sys.stderr.write('File not found')
            uuids = None
        else:
            uuids = ["'" + uuid.strip() + "'" for uuid in fdesc.readlines() if uuid.strip()]
            fdesc.close()
        return uuids

    def publish(self, rset=None):
        filename = self._cw.form['__file']
        etype = self._cw.form['__etype']
        uuids = self._read_uuid_file(filename)
        if uuids:
            rql = ('Any X WHERE X is %(etype)s, X identifier IN (%(uuids)s)'
                   % {'uuids': ', '.join(uuids), 'etype': etype})
            raise Redirect(self._cw.build_url(vid='list', rql=rql))
        raise Redirect(self._cw.base_url())
