# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubes.medicalexp.config import SUBJECT_CONTAINER, ASSESSMENT_CONTAINER
from unittest_schema import create_test_data


class MedicalexpContainersTC(CubicWebTC):
    """ Test proper behavior with respect to the Subject and Assessment containers. """

    def test_create_subject_container_instance(self):
        """ Container entities are created, according to the schema.
        """
        req = self.request()
        create_test_data(req)

    def test_static_structure_subject(self):
        cfg = SUBJECT_CONTAINER
        self.assertEqual((frozenset(['related_diagnostics', 'related_therapies',
                                     'taken_in_therapy', 'admission_of', 'step_of']),
                          frozenset(['Diagnostic', 'Therapy', 'DrugTake',
                                     'Admission', 'AdmissionStep'])),
                         cfg.structure(self.vreg.schema))

    def test_static_structure_assessment(self):
        cfg = ASSESSMENT_CONTAINER
        self.assertEqual(
            (frozenset(['results_files', 'configuration_files', 'uses', 'performed_on',
                        'generates', 'measure', 'file_entries']),
             frozenset(['GenericMeasure', 'TechnicalAnalysis', 'ExternalFile',
                        'FileSet', 'ScoreValue', 'File'])),
            cfg.structure(self.vreg.schema))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
