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

"""cubicweb-questionnaire schema"""

from yams.buildobjs import (EntityType, SubjectRelation, String, Int, Float, Date, Boolean, RichString)


class QuestionnaireRun(EntityType):
    user_ident = String(required=True, indexed=True, maxsize=64)
    datetime = Date()
    iteration = Int(indexed=True)
    completed = Boolean(indexed=True)
    valid = Boolean(indexed=True)
    instance_of = SubjectRelation('Questionnaire', cardinality='1*',
                                  inlined=True, composite='object')


class Questionnaire(EntityType):
    name = String(required=True, unique=True, maxsize=256)
    identifier = String(required=True, indexed=True, maxsize=64)
    type = String(maxsize=256, required=True)
    version = String(maxsize=16)
    language = String(maxsize=16)
    note = RichString(fulltextindexed=True)


class Question(EntityType):
    identifier = String(required=True, unique=True, indexed=True, maxsize=64)
    position = Int(indexed=True)
    text = String(maxsize=1024)
    type = String(maxsize=64)
    possible_answers = String()
    questionnaire = SubjectRelation('Questionnaire', cardinality='1*',
                                    inlined=True, composite='object')


class Answer(EntityType):
    value = Float(indexed=True)
    datetime = Date()
    question = SubjectRelation('Question', cardinality='1*', inlined=True, composite='object')
    questionnaire_run = SubjectRelation('QuestionnaireRun', cardinality='1*',
                                        inlined=True, composite='object')
