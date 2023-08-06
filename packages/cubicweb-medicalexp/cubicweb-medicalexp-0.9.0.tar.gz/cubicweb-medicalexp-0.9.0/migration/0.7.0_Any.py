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

rename_entity_type('Group', 'SubjectGroup')
add_relation_definition('SubjectGroup', 'related_studies', 'Study')


sync_schema_props_perms(('Subject', 'related_infos', 'ScoreValue'))
sync_schema_props_perms(('Subject', 'related_therapies', 'Therapy'))

sync_schema_props_perms(('Device', 'hosted_by', 'Center'))

sync_schema_props_perms('external_resources')
sync_schema_props_perms('results_file')

sync_schema_props_perms('related_study')

sync_schema_props_perms('subpart_of')

sync_schema_props_perms('broader_technique')

sync_schema_props_perms('taken_in_therapy')

sync_schema_props_perms(('ScoreValue', 'definition', 'ScoreDefinition'))

sync_schema_props_perms(('GenericTestRun', 'instance_of', 'GenericTest'))

sync_schema_props_perms(('Subject', 'concerned_by', 'Assessment'))

sync_schema_props_perms(('Center', 'holds', 'Assessment'))

sync_schema_props_perms('concerns')

sync_schema_props_perms(('ScoreValue', 'measure', 'GenericMeasure'))
sync_schema_props_perms(('ScoreValue', 'measure', 'GenericTestRun'))


add_relation_definition('Center', 'participates_in', 'Study')

change_attribute_type('Device', 'serialnum', 'String')

rename_entity_type('Group', 'SubjectGroup')

rename_attribute('Assessment', 'age_for_assessment', 'age_of_subject')

add_relation_definition('ProcessingRun', 'inputs', 'ScoreValue')
add_relation_definition('ProcessingRun', 'outputs', 'ScoreValue')
