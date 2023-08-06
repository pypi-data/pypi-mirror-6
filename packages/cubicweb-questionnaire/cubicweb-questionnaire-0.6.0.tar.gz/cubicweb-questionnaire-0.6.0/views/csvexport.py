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

from cubicweb.web.views.csvexport import CSVRsetView
from cubicweb.selectors import is_instance


class QuestionnaireCSVView(CSVRsetView):
    __select__ = CSVRsetView.__select__ & is_instance('QuestionnaireRun')

    def call(self):
        req = self._cw
        values = {}
        questions = {}
        for entity in self.cw_rset.entities():
            rset = self._cw.execute(
                'Any A, Q, SI, AV, AD, QI, QP, QT, QTY, QPA ORDERBY QP '
                'WHERE QR is QuestionnaireRun, QR concerns S, S identifier SI, QR eid %(e)s, '
                'A questionnaire_run QR, A question Q, '
                'A value AV, A datetime AD, '
                'Q identifier QI, Q position QP, Q text QT, '
                'Q type QTY, Q possible_answers QPA',
                {'e': entity.eid})
            for ind, row in enumerate(rset.rows):
                answer = rset.get_entity(ind, 0)
                question = rset.get_entity(ind, 1)
                subject = rset[ind][2]
                values.setdefault(subject, {})[question.identifier] = answer.value
                questions[question.identifier] = question.text
        rows = []
        headers = ['"subject_id"',]
        headers.extend(['"%s"' % q for q in questions.values()])
        rows.append(headers)
        for subject, _values in values.iteritems():
            row = [subject]
            for question_id in questions:
                row.append(_values.get(question_id))
            rows.append(row)
        writer = self.csvwriter()
        writer.writerows(rows)
