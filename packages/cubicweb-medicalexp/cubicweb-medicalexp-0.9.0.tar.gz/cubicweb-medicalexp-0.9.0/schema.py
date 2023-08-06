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

"""cubicweb-medicalexp schema"""

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, RichString, Int, Float, Date, Boolean)
from yams.constraints import BoundaryConstraint, Attribute

_ = unicode


###############################################################################
### PROJECT/SUBJECT SPECIFIC ENTITIES #########################################
###############################################################################
class Subject(EntityType):
    """ The subject """
    identifier = String(required=True, unique=True, fulltextindexed=True,
                        indexed=True, maxsize=64)
    surname = String(fulltextindexed=True, maxsize=256)
    firstname = String(fulltextindexed=True, maxsize=256)
    gender = String(required=True, indexed=True,
                    vocabulary=('male', 'female', 'unknown'))
    date_of_birth = Date()
    handedness = String(required=True, indexed=True,
                        vocabulary=('right', 'left', 'ambidextrous', 'mixed', 'unknown'))
    related_studies = SubjectRelation('Study', cardinality='**')
    related_groups = SubjectRelation('SubjectGroup', cardinality='**')
    related_diseases = SubjectRelation('Disease', cardinality='**')
    related_lesions = SubjectRelation('BodyLocation', cardinality='**')
    related_diagnostics = SubjectRelation('Diagnostic', cardinality='**', composite='subject')
    related_therapies = SubjectRelation('Therapy', cardinality='**', composite='subject')


class Study(EntityType):
    """ The project """
    name = String(required=True, indexed=True, maxsize=256)
    data_filepath = String()
    description = RichString(fulltextindexed=True)
    keywords = String(maxsize=1024)
    themes = SubjectRelation('Theme', cardinality='**')
    substudy_of = SubjectRelation('Study', cardinality='?*', inlined=True)


class Theme(EntityType):
    """ Study theme, etiology """
    name = String(required=True, indexed=True, maxsize=256)
    description = RichString(fulltextindexed=True)


class SubjectGroup(EntityType):
    """ Group of subject """
    identifier = String(required=True, unique=True, indexed=True, maxsize=64)
    name = String(maxsize=64, required=True, indexed=True)
    related_studies = SubjectRelation('Study', cardinality='**')


class Admission(EntityType):
    """ Admission info on a subject/study"""
    admission_date = Date(description=_('Date of admission of the patient in the study'))
    admission_end_date = Date(description=_('Date when the patient leaves the study'),
                              constraints=[BoundaryConstraint('>=', Attribute('admission_date'))])
    admission_of = SubjectRelation('Subject', cardinality='1*', composite='object', inlined=True)
    admission_in = SubjectRelation('Study', cardinality='1*', inlined=True)
    description = RichString(fulltextindexed=True, description=_('Additional admission infos'))


class AdmissionStep(EntityType):
    """ Possible steps of an Admission"""
    step_date = Date(description=_('Date of step of admission'))
    name = String(required=True, indexed=True, maxsize=256,
                  description=_('Name of the admission step'))
    step_of = SubjectRelation('Admission', cardinality='1*', composite='object', inlined=True)
    description = RichString(fulltextindexed=True, description=_('Additional admission infos'))


###############################################################################
### PROJECT MANAGEMENT ENTITIES ###############################################
###############################################################################
class Investigator(EntityType):
    """ Investigator of a study / PI """
    identifier = String(required=True, unique=True, indexed=True, maxsize=64)
    firstname = String(maxsize=256)
    lastname = String(maxsize=256)
    title = String(maxsize=16)
    institution = String(maxsize=256)
    department = String(maxsize=256)

class Center(EntityType):
    """ A center used for study """
    identifier = String(required=True, unique=True, indexed=True, maxsize=64)
    name = String(maxsize=256, required=True)
    department = String(maxsize=256)
    city = String(maxsize=64)
    country = String(maxsize=64)

class Device(EntityType):
    """ Device used in experiments/assessments """
    name = String(maxsize=256, required=True)
    manufacturer = String(maxsize=256)
    model = String(maxsize=256)
    serialnum = String(maxsize=256)
    configurations = SubjectRelation('Configuration', cardinality='*1')
    hosted_by = SubjectRelation('Center', cardinality='1*', inlined=True, composite='object')

class Configuration(EntityType):
    """ Configuration of a device """
    start_datetime = Date()
    end_datetime = Date()
    configuration_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                       cardinality='**', composite='subject')

class Protocol(EntityType):
    """ A protocol for a study or a measure """
    identifier = String(required=True, unique=True, indexed=True, maxsize=64)
    name = String(internationalizable=True)
    related_study = SubjectRelation('Study', cardinality='1*', inlined=True, composite='object')
    start_datetime = Date()
    end_datetime = Date()
    configuration_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                          cardinality='**', composite='subject')


###############################################################################
### GLOSSARY ENTITIES #########################################################
###############################################################################
class Disease(EntityType):
    identifier = String(required=True, unique=True, indexed=True, maxsize=1024)
    name = String(required=True, fulltextindexed=True,
                  internationalizable=True, maxsize=2048)
    mesh_id = String(maxsize=64)
    icd10 = String(maxsize=64)
    description = RichString(fulltextindexed=True)
    lesion_of = SubjectRelation('BodyLocation', cardinality='**')


class BodyLocation(EntityType):
    identifier = String(required=True, unique=True, indexed=True, maxsize=1024)
    name = String(required=True, fulltextindexed=True,
                  internationalizable=True, maxsize=2048)
    mesh_id = String(maxsize=64)
    description = RichString(fulltextindexed=True)
    subpart_of = SubjectRelation('BodyLocation', cardinality='?*', inlined=True, composite='object')


class MedicalTechnique(EntityType):
    identifier = String(required=True, unique=True, indexed=True, maxsize=1024)
    name = String(required=True, fulltextindexed=True,
                  internationalizable=True, maxsize=2048)
    type = String(vocabulary=[_('diagnostic'), _('analysis')])
    description = RichString(fulltextindexed=True)
    broader_technique = SubjectRelation('MedicalTechnique', cardinality='?*', inlined=True, composite='object')


###############################################################################
### DIAGNOSTIC AND ANALYSIS ###################################################
###############################################################################
class Diagnostic(EntityType):
    """ Diagnostic attributes and links.
    Diagnostic may be based on specific measures, and holds a conclusion
    on BodyLocation/Disease"""
    diagnostic_date = Date()
    conclusion = String(maxsize=256, fulltextindexed=True)
    diagnostic_location = SubjectRelation('BodyLocation', cardinality='1*', inlined=True)
    diagnosed_disease = SubjectRelation('Disease', cardinality='1*', inlined=True)
    technique_type = SubjectRelation('MedicalTechnique', cardinality='?*', inlined=True)
    leads_to_therapies = SubjectRelation('Therapy', cardinality='**')
    technical_analysis = SubjectRelation('TechnicalAnalysis', cardinality='**')
    based_on = SubjectRelation('GenericMeasure', cardinality='**')


class TechnicalAnalysis(EntityType):
    """ Analysis attributes and links.
    An analysis is done with a given technique and give some results
    """
    analysis_date = Date()
    results = String(maxsize=2048, fulltextindexed=True)
    conclusion = String(maxsize=256, fulltextindexed=True)
    technique_type = SubjectRelation('MedicalTechnique', cardinality='1*', inlined=True)
    performed_in_therapy = SubjectRelation('Therapy', cardinality='?*', inlined=True)


###############################################################################
### THERAPY AND DRUG ##########################################################
###############################################################################
class Therapy(EntityType):
    """ Therapy attributes and links"""
    start_date = Date()
    stop_date = Date()
    relevant_anomaly = String(maxsize=1024)
    therapy_for = SubjectRelation('Disease', cardinality='**')
    based_on_diagnostic = SubjectRelation('Diagnostic', cardinality='**')
    description = RichString(fulltextindexed=True)

class DrugTake(EntityType):
    """ Drug take """
    start_taking_date = Date(required=True)
    # Stop taking date is not required as the treatment could still exist
    stop_taking_date = Date()
    # Order for multiple drugs if it is relevant
    take_order = Int()
    dosis = Int()
    unit = Int()#quantity = dosis * unit
    number_of_cycles = Int()
    dosis_percentage = Float(description=u'dosis percentage, w.r.t. the expansion cohort')
    reduced_dosis = Boolean()
    taken_in_therapy = SubjectRelation('Therapy', cardinality='1*', inlined=True, composite='object')
    drug = SubjectRelation('Drug', cardinality='1*', inlined=True)

class Drug(EntityType):
    """ Drug attributes """
    identifier = String(required=True, unique=True, indexed=True, maxsize=1024)
    name = String(required=True, maxsize=2048)
    description = RichString(fulltextindexed=True)
    # Ids
    pubchem_id = String(maxsize=64)
    drugbank_id = String(maxsize=128)
    unii_id = String(maxsize=128)
    cas_number = String(maxsize=128)
    iupac_name = String(maxsize=128)
    routes_of_administration = String(maxsize=2048)
    metabolism = String(maxsize=2048)
    drug_for = SubjectRelation('Disease', cardinality='**')
    acts_on = SubjectRelation('BodyLocation', cardinality='**')


###############################################################################
### ASSESSMENT/MEASURE ENTITIES ###############################################
###############################################################################
class Assessment(EntityType):
    """ Store information about a visit """
    datetime = Date()
    age_of_subject = Int(indexed=True)
    timepoint = String(maxsize=64)
    related_study = SubjectRelation('Study', cardinality='1*', inlined=True)
    results_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                    cardinality='**', composite='subject')
    configuration_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                          cardinality='**', composite='subject')


class GenericMeasure(EntityType):
    """ Generic measure used to store non base type measures
    (e.g. referential, numerical values...) """
    name = String(maxsize=256, required=True)
    type = String(maxsize=256, required=True)
    related_study = SubjectRelation('Study', cardinality='1*', inlined=True,
                                    composite='object')
    other_studies = SubjectRelation('Study', cardinality='**')
    results_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                    cardinality='**', composite='subject')
    configuration_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                          cardinality='**', composite='subject')

class ProcessingRun(EntityType):
    name = String(maxsize=256)
    tool = String(maxsize=256)
    datetime = Date()
    category = String(maxsize=256)
    version = String(maxsize=64)
    parameters = String(maxsize=256)
    note = RichString(fulltextindexed=True)
    followed_by = SubjectRelation('ProcessingRun' , cardinality='??', inlined=True)
    results_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                    cardinality='**', composite='subject')
    configuration_files = SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                       cardinality='**', composite='subject')


###############################################################################
### SATELLITE ENTITIES ########################################################
###############################################################################
class FileSet(EntityType):
    """ A composite resource file set """
    name = String(maxsize=256, required=True)
    file_entries = SubjectRelation(('File', 'ExternalFile'),
                                   cardinality='**', composite='subject')


class ExternalFile(EntityType):
    """ An external resource file (e.g. an absolute/relative filepath)
    """
    name = String(maxsize=256)
    # If not absolute_path, use the data_filepath of the study
    absolute_path = Boolean(default=True)
    filepath = String(required=True, indexed=True, maxsize=256)
    study_path = SubjectRelation('Study', cardinality='?*', inlined=True)


class ScoreDefinition(EntityType):
    """ A score definition """
    name = String(maxsize=256, required=True,  fulltextindexed=True)
    category = String(maxsize=64, fulltextindexed=True)
    type = String(required=True, indexed=True, vocabulary=('string', 'numerical', 'logical'),)
    unit = String(maxsize=16, indexed=True)
    possible_values = String(maxsize=256, fulltextindexed=True)

# XXX Two different etypes for string/numerical values ?
class ScoreValue(EntityType):
    """ A score value """
    definition = SubjectRelation('ScoreDefinition', cardinality='1*', inlined=True, composite='object')
    text = String(maxsize=2048, fulltextindexed=True)
    value = Float(indexed=True)
    datetime = Date()

class ScoreGroup(EntityType):
    """ A group of score values that should be considered together """
    identifier = String(required=True, unique=True, indexed=True, maxsize=64)
    scores = SubjectRelation('ScoreValue', cardinality='**')


###############################################################################
### RELATIONS #################################################################
###############################################################################
class concerned_by(RelationDefinition):
    subject = 'Subject'
    object = 'Assessment'
    cardinality = '*+'

class conducted_by(RelationDefinition):
    subject = 'Assessment'
    object = 'Investigator'
    cardinality = '**'

class holds(RelationDefinition):
    subject = 'Center'
    object = 'Assessment'
    cardinality = '*1'
    composite='subject'

class inputs(RelationDefinition):
    subject = 'ProcessingRun'
    object = 'ScoreValue'
    cardinality = '**'

class outputs(RelationDefinition):
    subject = 'ProcessingRun'
    object = 'ScoreValue'
    cardinality = '**'

class related_processing(RelationDefinition):
    subject = 'Assessment'
    object = 'ProcessingRun'
    cardinality = '**'

class performed_on(RelationDefinition):
    subject = 'TechnicalAnalysis'
    object = 'GenericMeasure'
    cardinality = '**'
    composite = 'object'

class concerns(RelationDefinition):
    subject = 'GenericMeasure'
    object = ('Subject', 'SubjectGroup')
    cardinality = '1*'
    inlined = True

class uses(RelationDefinition):
    subject = 'Assessment'
    object = 'GenericMeasure'
    cardinality = '**'
    composite = 'subject'

class generates(RelationDefinition):
    subject = 'Assessment'
    object = 'GenericMeasure'
    cardinality = '?*'
    composite = 'subject'

class measure(RelationDefinition):
    subject = 'ScoreValue'
    object = 'GenericMeasure'
    cardinality = '?*'
    inlined = True
    composite='object'

class protocols(RelationDefinition):
    subject = ('Assessment', 'ScoreDefinition', 'ScoreGroup',
               'Diagnostic', 'TechnicalAnalysis')
    object = 'Protocol'
    cardinality = '**'

class participates_in(RelationDefinition):
    subject = 'Center'
    object = 'Study'
    cardinality = '**'


def post_build_callback(schema):
    from cubes.medicalexp.config import SUBJECT_CONTAINER, ASSESSMENT_CONTAINER
    SUBJECT_CONTAINER.define_container(schema)
    ASSESSMENT_CONTAINER.define_container(schema)
