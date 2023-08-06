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

"""cubicweb-medicalexp entity's classes"""
import os.path as osp

from logilab.common.date import ustrftime

from cubicweb.selectors import is_instance
from cubicweb.view import EntityAdapter
from cubicweb.entities import AnyEntity, fetch_config

from cubes.medicalexp.config import SUBJECT_CONTAINER, ASSESSMENT_CONTAINER


class Subject(AnyEntity):
    __regid__ = 'Subject'
    fetch_attrs, fetch_order = fetch_config(('gender', 'handedness'))
    container_config = SUBJECT_CONTAINER

    def dc_title(self):
        return self.identifier

    @property
    def symbol(self):
        if self.gender == 'male':
            return '&#x2642;'
        elif self.gender == 'female':
            return '&#x2640;'
        else:
            return '&nbsp;'

    @property
    def age_of_subjects(self):
        rset = self._cw.execute('Any A WHERE S concerned_by X, S eid %(e)s, X age_of_subject A',
                                {'e': self.eid})
        if rset.rowcount:
            return (min(r[0] for r in rset), max(r[0] for r in rset))
        else:
            return None, None

    def display_age_of_subjects(self):
        age_min, age_max = self.age_of_subjects
        if age_min and age_max and age_min != age_max:
            age = '%s-%s' % (age_min, age_max)
        elif age_min:
            age = str(age_min)
        elif age_max:
            age = str(age_max)
        else:
            age = None
        return age

    @property
    def related_centers(self):
        rset = self._cw.execute('DISTINCT Any X WHERE X holds A, S concerned_by A, S eid %(e)s',
                                {'e': self.eid})
        return list(rset.entities())


class Center(AnyEntity):
    __regid__ = 'Center'

    def dc_title(self):
        return self.name


class Study(AnyEntity):
    __regid__ = 'Study'

    def dc_title(self):
        return self.name


class Device(AnyEntity):
    __regid__ = 'Device'

    def dc_title(self):
        return self.name


class SubjectGroup(AnyEntity):
    __regid__ = 'SubjectGroup'

    def dc_title(self):
        return self.name


class Assessment(AnyEntity):
    __regid__ = 'Assessment'
    container_config = ASSESSMENT_CONTAINER

    def dc_title(self):
        return '%s (%s)' % (self._cw._('Assessment'), self.datetime)


class Protocol(AnyEntity):
    __regid__ = 'Protocol'

    def dc_title(self):
        if self.name:
            return '%s (%s)' % (self.name, self.identifier)
        return self.identifier


class ProcessingRun(AnyEntity):
    __regid__ = 'ProcessingRun'

    def dc_title(self):
        return u'ProcessingRun (%s) - %s' % (self.category, self.name)


class ScoreDefinition(AnyEntity):
    __regid__ = 'ScoreDefinition'

    def dc_title(self):
        return u'%s (%s)' % (self.category, self.name)


class ScoreValue(AnyEntity):
    __regid__ = 'ScoreValue'

    def dc_title(self):
        _def = self.definition[0]
        _def_title = self._cw._(_def.dc_title())
        return u'%s : %s (%s)' % (_def_title, self.value, self.datetime)

    @property
    def subject(self):
        if self.reverse_related_infos:
            return self.reverse_related_infos[0]
        if self.measure:
            return self.measure[0].concerns[0]

    @property
    def complete_value(self):
        return self.value or self.text


class ExternalFile(AnyEntity):
    __regid__ = 'ExternalFile'

    def dc_title(self):
        return self.name

    @property
    def full_filepath(self):
        if self.absolute_path:
            return self.filepath
        # Use the relatedstudy
        if not self.related_study:
            raise ValueError('The ExternalFile is not related to a study, '
                             'but as a relative filepath')
        return osp.join(self.related_study[0].data_filepath, self.filepath)


class ScoreGroup(AnyEntity):
    __regid__ = 'ScoreGroup'

    def get_score(self, name):
        return [(v, v.definition[0]) for v in self.scores if v.definition[0].name == name]


class Disease(AnyEntity):
    __regid__ = 'Disease'

    def dc_title(self):
        return self.name


class BodyLocation(AnyEntity):
    __regid__ = 'BodyLocation'

    def dc_title(self):
        if not self.subpart_of:
            return self.name
        return '%s (%s)' % (self.subpart_of[0].dc_title(), self.name)


class MedicalTechnique(AnyEntity):
    __regid__ = 'MedicalTechnique'

    def dc_title(self):
        return self.name


class TechnicalAnalysis(AnyEntity):
    __regid__ = 'TechnicalAnalysis'

    def dc_title(self):
        return u'%s : %s' % (self._cw._('TechnicalAnalysis'), self.technique_type[0].dc_title())


class Diagnostic(AnyEntity):
    __regid__ = 'Diagnostic'

    def dc_title(self):
        return u'%s : %s - %s' % (self._cw._('Diagnostic'),
                                  self.diagnostic_location[0].dc_title(),
                                  self.diagnosed_disease[0].dc_title())


class DrugTake(AnyEntity):
    __regid__ = 'DrugTake'

    def dc_title(self):
        return u'%s - %s' % (self._cw._('DrugTake'), self.drug[0].dc_title())


class Therapy(AnyEntity):
    __regid__ = 'Therapy'

    def dc_title(self):
        title = self._cw._('Therapy')
        if self.therapy_for:
            title += ' (%s)' % self.therapy_for[0].dc_title()
        return title


class Admission(AnyEntity):
    __regid__ = 'Admission'

    def dc_title(self):
        title = '%s %s' % (self._cw._('Admission'), self.admission_in[0].dc_title())
        dates = []
        if self.admission_date:
            dates.append(ustrftime(self.admission_date, '%Y,%m,%d'))
        if self.admission_end_date:
            dates.append(ustrftime(self.admission_end_date, '%Y,%m,%d'))
        if dates:
            title += ' (%s)' % '/'.join(dates)
        return title


class AdmissionStep(AnyEntity):
    __regid__ = 'AdmissionStep'

    def dc_title(self):
        title = self.name
        if self.step_date:
            title += ' (%s)' % self.step_date
        return title

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.register(SUBJECT_CONTAINER.build_container_protocol(vreg.schema))
    vreg.register(ASSESSMENT_CONTAINER.build_container_protocol(vreg.schema))
