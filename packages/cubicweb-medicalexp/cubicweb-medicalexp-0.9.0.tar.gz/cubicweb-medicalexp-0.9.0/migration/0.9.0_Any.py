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


sync_schema_props_perms('ScoreDefinition')
sync_schema_props_perms('ScoreValue')
add_entity_type('Diagnostic')
add_entity_type('TechnicalAnalysis')

remove_entity_type('ExternalResource')
add_entity_type('FileSet')
add_entity_type('ExternalFile')
add_relation_type('configuration_files')


drop_attribute('Therapy', 'identifier')
drop_attribute('Assessment', 'identifier')
drop_attribute('GenericMeasure', 'identifier')

add_relation_type('substudy_of')

add_entity_type('Admission')
add_entity_type('AdmissionStep')

drop_entity_type('GenericTestRun')
drop_entity_type('GenericTest')

sync_schema_props_perms('inputs')
sync_schema_props_perms('outputs')
sync_schema_props_perms('performed_on')
sync_schema_props_perms('concerns')
sync_schema_props_perms('uses')
sync_schema_props_perms('generates')
sync_schema_props_perms('measure')

drop_relation_definition(('Subject', 'related_infos', 'ScoreValue'))
sync_schema_props_perms(('GenericMeasure', 'related_study', 'Study'))
sync_schema_props_perms(('Subject', 'concerned_by', 'Assessment'))
sync_schema_props_perms('performed_on')

add_cube('container')

add_relation_definition('Diagnostic', 'technical_analysis', 'TechnicalAnalysis')
drop_relation_definition('Diagnostic', 'performed_on', 'GenericMeasure')
add_relation_definition('Diagnostic', 'based_on', 'GenericMeasure')
