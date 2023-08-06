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

"""cubicweb-questionnaire entity's classes"""

from cubicweb.entities import AnyEntity, fetch_config


class QuestionnaireRun(AnyEntity):
    __regid__ = 'QuestionnaireRun'
    fetch_attrs, fetch_order = fetch_config(('instance_of',))

    def dc_title(self):
        return '%s - (%s)' % (self._cw._('QuestionnaireRun'), self.instance_of[0].dc_title())

    @property
    def formatted_datetime(self):
        if not self.datetime:
            return 'missing'
        else:
            return self.datetime

    @property
    def image_url(self):
        return self._cw.data_url('questionnaire.jpg')


class Answer(AnyEntity):
    __regid__ = 'Answer'
    fetch_attrs, fetch_order = fetch_config(('value', 'question',
                                             'questionnaire_run'))

    def dc_title(self):
        return '%s - (%s)' % (self._cw._('Answer'), self.questionnaire_run[0].dc_title())

    @property
    def computed_value(self):
        value = self.value
        question = self.question[0]
        if question.type == 'text' and question.possible_answers:
            return question.possible_answers.split('\x1f')[int(value)]
        return value


class Question(AnyEntity):
    __regid__ = 'Question'
    fetch_attrs, fetch_order = fetch_config(('identifier', 'text', 'type',
                                             'possible_answers',
                                             'questionnaire'))
    @property
    def displayable_possible_answers(self):
        return self.possible_answers if self.type == 'text' else u'-'
