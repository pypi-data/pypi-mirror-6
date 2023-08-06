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

add_entity_type('Protocol')
add_entity_type('ScoreGroup')
add_entity_type('Disease')
add_entity_type('BodyLocation')
add_entity_type('MedicalTechnique')
add_entity_type('Therapy')
add_entity_type('DrugTake')
add_entity_type('Drug')
add_relation_type('protocols')

add_relation_definition('Subject', 'related_diseases', 'Disease')
add_relation_definition('Subject', 'related_lesions', 'BodyLocation')
add_relation_definition('Subject', 'related_therapies', 'Therapy')

add_relation_definition('Protocol', 'external_resources', 'ExternalResource')
add_relation_definition('Disease', 'lesion_of', 'BodyLocation')
add_relation_definition('BodyLocation', 'subpart_of', 'BodyLocation')

add_relation_definition('MedicalTechnique', 'broader_technique', 'MedicalTechnique')
add_relation_definition('Therapy', 'therapy_for', 'Disease')

add_relation_definition('DrugTake', 'taken_in_therapy', 'Therapy')
add_relation_definition('DrugTake', 'drug', 'Drug')

add_relation_definition('Drug', 'drug_for', 'Disease')
add_relation_definition('Drug', 'acts_on', 'BodyLocation')

drop_attribute('Assessment', 'protocol')

add_relation_definition('ScoreGroup', 'scores', 'ScoreValue')

