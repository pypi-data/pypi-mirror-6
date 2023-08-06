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

""" Entities test """

from datetime import date

from cubicweb.devtools.testlib import CubicWebTC, ValidationError


class MedicalexpEntitiesTC(CubicWebTC):

    def test_admission_title(self):
        req = self.request()
        subj = req.create_entity('Subject', identifier=u'12345HT1',
                                 gender=u'unknown', handedness=u'mixed')
        study = req.create_entity('Study', name=u'Test study')
        admission = req.create_entity('Admission', admission_date=date(1970, 11, 12),
                                      admission_of=subj, admission_in=study)
        self.assertEqual(admission.dc_title(), 'Admission Test study (1970,11,12)')

    def test_admission_constraint(self):
        req = self.request()
        subj = req.create_entity('Subject', identifier=u'12345HT1',
                                 gender=u'unknown', handedness=u'mixed')
        study = req.create_entity('Study', name=u'Test study')
        with self.assertRaises(ValidationError):
            admission = req.create_entity('Admission',
                                          admission_date=date(1970, 11, 12),
                                          admission_end_date=date(1968, 11, 12),
                                          admission_of=subj, admission_in=study)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
