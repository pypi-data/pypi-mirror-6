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

from datetime import date
from cubicweb.devtools.testlib import CubicWebTC

def create_test_data(req):
    t_subj = req.create_entity('Subject', identifier=u'12345HT1', gender=u'unknown',
                               handedness=u'mixed')
    t_score_val = req.create_entity('ScoreValue', text=u'test value')
    t_score_def = req.create_entity('ScoreDefinition', name=u'Test score',
                                    type=u'string', reverse_definition=t_score_val)
    t_ext_res = req.create_entity('ExternalFile', name=u'Test ext res',
                                  filepath=u'/test/ext/res/filepath')
    t_gen_meas = req.create_entity('GenericMeasure',
                                   name=u'Test measure', type=u'string', concerns=t_subj,
                                   results_files=t_ext_res,
                                   reverse_measure=t_score_val)
    t_rel_study = req.create_entity('Study', name=u'Test study',
                                    data_filepath=u'/test/study/data/filepath/',
                                    reverse_related_study=[t_gen_meas, t_ext_res])
    t_therapy = req.create_entity('Therapy',
                                  reverse_related_therapies=t_subj)
    t_drug = req.create_entity('Drug', identifier=u'Test drug id', name=u'Test drug name')
    t_drug_take = req.create_entity('DrugTake', start_taking_date=date(1970, 11, 12),
                                    taken_in_therapy=t_therapy, drug=t_drug)


class MedicalexpSchemaTC(CubicWebTC):
    """ Test proper behavior with respect to the composite relations. """

    def setup_database(self):
        """ Several entities involving composite relations are created,
            according to the schema.
        """
        req = self.request()
        create_test_data(req)

    def test_cleanup_on_subject_deletion(self):
        """ Test that on Subject deletion, ScoreValue, ExternalFile,
            Therapy and DrugTake are deleted, and that Study is
            not deleted.
        """
        req = self.request()
        t_subj = req.execute('Any X WHERE X is Subject').get_entity(0, 0)
        # Remove the associated GenericMeasure first:
        req.execute('DELETE GenericMeasure X WHERE X concerns Y, Y eid %(subjid)s',
                    {'subjid': t_subj.eid})
        req.execute('DELETE Subject X WHERE X eid %(subjid)s', {'subjid': t_subj.eid})
        self.commit()
        db_score_value = req.execute('Any X WHERE X is ScoreValue')
        if db_score_value:
            self.fail('The ScoreValue was not deleted')
        db_gen_meas = req.execute('Any X WHERE X is GenericMeasure')
        if db_gen_meas:
            self.fail('The GenericMeasure was not deleted')
        db_ext_res = req.execute('Any X WHERE X is ExternalFile')
        if db_ext_res:
            self.fail('The ExternalFile was not deleted')
        db_therapy = req.execute('Any X WHERE X is Therapy')
        if db_therapy:
            self.fail('The Therapy was not deleted')
        db_drug_take = req.execute('Any X WHERE X is DrugTake')
        if db_drug_take:
            self.fail('The DrugTake was not deleted')
        db_study = req.execute('Any X WHERE X is Study')
        if not db_study:
            self.fail('The Study was deleted')

    def test_cleanup_on_study_deletion(self):
        """ Test that on Study deletion, GeneriMeasure, ExternalFile
            and ScoreValue (if the `measure` relation between
            GenericMeasure and ScoreValue is enabled) are deleted.
        """
        req = self.request()
        t_study = req.execute('Any X WHERE X is Study').get_entity(0, 0)
        req.execute('DELETE Study X WHERE X eid %(studeid)s', {'studeid': t_study.eid})
        self.commit()
        db_gen_meas = req.execute('Any X WHERE X is GenericMeasure')
        if db_gen_meas:
            self.fail('The GenericMeasure was not deleted')
        db_score_val = req.execute('Any X WHERE X is ScoreValue')
        if db_score_val:
            self.fail('The ScoreValue was not deleted')
        db_ext_res = req.execute('Any X WHERE X is ExternalFile')
        if db_ext_res:
            self.fail('The ExternalFile was not deleted')

    def test_cleanup_on_score_def_deletion(self):
        """ Test that when ScoreDefinition is deleted, ScoreValue is deleted,
            GenericMeasure is not deleted, even when the `measure` relation
            between ScoreValue and GenericMeasure is enabled.
        """
        req = self.request()
        t_score_def = req.execute('Any X WHERE X is ScoreDefinition').get_entity(0, 0)
        req.execute('DELETE ScoreDefinition X WHERE X eid %(scdefeid)s',
                    {'scdefeid': t_score_def.eid})
        self.commit()
        db_score_value = req.execute('Any X WHERE X is ScoreValue')
        if db_score_value:
            self.fail('The ScoreValue was not deleted')
        db_gen_meas = req.execute('Any X WHERE X is GenericMeasure')
        if not db_gen_meas:
            self.fail('The GenericMeasure was deleted')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
