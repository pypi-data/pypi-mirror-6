# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

""" Schema test """

from cubicweb.devtools.testlib import CubicWebTC

class QuestionnaireSchemaTC(CubicWebTC):
    """ Test proper behavior with respect to the composite relations. """
    def setup_database(self):
        """ Several entities involving composite relations are created,
            according to the schema.
        """
        req = self.request()
        t_questionnaire = req.create_entity('Questionnaire', name=u'Test quiz',
                                            identifier=u'test_quiz_id',
                                            type=u'test')
        t_qrun = req.create_entity('QuestionnaireRun',
                                   user_ident=u'test_qrun_uident',
                                   instance_of=t_questionnaire)
        t_question = req.create_entity('Question', identifier=u'test_question', position=1,
                                       text=u'What is the TSH concentration?',
                                       questionnaire=t_questionnaire)
        t_answer = req.create_entity('Answer', value=.45, question=t_question,
                                     questionnaire_run=t_qrun)

    def test_cleanup_on_qrun_delete(self):
        """ Test that on QuestionnaireRun deletion, the Answer
            is deleted.
        """
        req = self.request()
        t_qrun = req.execute('Any X WHERE X is QuestionnaireRun').get_entity(0, 0)
        db_answer = req.execute('Any X WHERE X is Answer')
        if not db_answer:
            self.fail('No Answer was found in the database')
        req.execute('DELETE QuestionnaireRun X WHERE X eid %(qruneid)s',
                    {'qruneid': t_qrun.eid})
        self.commit()
        db_answer = req.execute('Any X WHERE X is Answer')
        if db_answer:
            self.fail('The Answer was not deleted.')

    def test_cleanup_on_question_delete(self):
        """ Test that on Question deletion, the Answer
            is deleted.
        """
        req = self.request()
        t_question = req.execute('Any X WHERE X is Question').get_entity(0, 0)
        db_answer = req.execute('Any X WHERE X is Answer')
        if not db_answer:
            self.fail('No Answer was found in the database')
        req.execute('DELETE Question X WHERE X eid %(questeid)s',
                    {'questeid': t_question.eid})
        self.commit()
        db_answer = req.execute('Any X WHERE X is Answer')
        if db_answer:
            self.fail('The Answer was not deleted.')

    def test_cleanup_on_questionnaire_delete(self):
        """ Test that on Question deletion, the QuestionnaireRun
            and Question are deleted.
        """
        req = self.request()
        t_quiz = req.execute('Any X WHERE X is Questionnaire').get_entity(0, 0)
        db_qrun = req.execute('Any X WHERE X is QuestionnaireRun')
        db_question = req.execute('Any X WHERE X is Question')
        if not (db_qrun and db_question):
            self.fail('Some Question or QuestionnaireRun are missing from the database')
        req.execute('DELETE Questionnaire X WHERE X eid %(questeid)s',
                    {'questeid': t_quiz.eid})
        self.commit()
        db_qrun = req.execute('Any X WHERE X is QuestionnaireRun')
        if db_qrun:
            self.fail('The QuestionnaireRun was not deleted.')
        db_question = req.execute('Any X WHERE X is Question')
        if db_question:
            self.fail('The Question was not deleted.')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
