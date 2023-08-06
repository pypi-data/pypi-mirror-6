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

"""cubicweb-brainomics postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

set_property('ui.site-title', 'Brainomics')

# Create cards
create_entity('Card', content_format=u'text/html', title=u'index',
              content=u"""<div class="page-header"><h1>What is it?<small> And who are we?</small></h1></div>
              <p>The BRAINOMICS project is one of the projects chosen by the Agence nationale de la recherche (ANR) in the bioinformatics call of the Investissements d'avenir program. This website is a demonstration of the project based on the Localizer data (courtesy of P. Pinel, S. Dehaene, T. Bourgeron and D. Lebihan) and allows complex query and various visualization of the data.
This demo is for now only accessible on the Neurospin network.</p>
<p>This prototype was developed by V. Michel, Y. Schwartz, D. Papadopoulos and V. Frouin</p>
<p><span class="badge badge-important">This website is still in beta. Comments are welcome!</span></p>
<p> <strong>Feel free to play with it! Use the RQL <i>Search</i> field in the bar at the top of the page.</strong></p>""")

create_entity('Card', content_format=u'text/html', title=u'rqlexamples',
              content=u'''<ul>
              <li>Query all the subjects of the database
              <pre>Any S WHERE S is Subject</pre></li>
              <li>Query all right-handed subjects of the database
              <pre>Any S WHERE S is Subject, S handedness "right"</pre></li>
              <li>Query all the right-handed female subjects of the database
              <pre>Any S WHERE S is Subject, S handedness "right", S gender "female"</pre></li>
              <li>Query all the scans of male subjects
              <pre>Any X WHERE S is Subject, S gender "male", X is Scan, X concerns S</pre></li>
              <li>Query all female subjects that have a score greater than 4.O for the "algebre" question of the Localizer questionnary (Question number 2), and return both subject identifier and score
              <pre>Any I,V WHERE S is Subject, S identifier I, S gender "female", X is QuestionnaireRun, X concerns S, A is Answer, A questionnaire_run X, A question Q, Q text "algebre", A value V, A value > 4</pre></li>
              <li>Query 100 Cmap scans of subjects that have a score greater than 4.O for the "algebre" question of the Localizer questionnary (Question number 2)
              <pre>Any SA LIMIT 100 WHERE S is Subject, X is QuestionnaireRun, X concerns S, A is Answer, A questionnaire_run X, A question Q, Q text "algebre", A value > 4, SA is Scan, SA concerns S, SA type "c map"</pre></li>
              <li>Query all the Tmap scans for the "auditory calculation" contrast of subjects along with their Genomics data, when we have acquired data for Snps on the gene "CFB":
              <pre>Any S,SCF,FGEN WHERE S is Subject, SC is Scan, SC type "t map", SC label "auditory calculation", SC concerns S, SC filepath SCF, GEN is GenomicMeasure, GEN filepath FGEN, GEN concerns S, GEN platform P, P related_snps SN, G is Gene, G name "CFB", G start_position GSA, G stop_position GSO, SN position SP HAVING SP > GSA, SP &lt; GSO</pre></li>
              </ul>''')


create_entity('Card', content_format=u'text/html', title=u'license',
              content=u"... License text ...")
