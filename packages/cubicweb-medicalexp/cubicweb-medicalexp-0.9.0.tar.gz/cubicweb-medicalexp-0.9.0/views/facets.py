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

"""cubicweb-medicalexp views/forms/actions/components for web ui"""
from cubicweb.web import facet
from cubicweb.selectors import is_instance


############################################################################
### SUBJECTS ###############################################################
############################################################################
class SubjectGenderFacet(facet.AttributeFacet):
    __regid__ = 'subject-gender-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Subject')
    order = 1
    rtype = 'gender'
    title = _('Gender')

class SubjectHandednessFacet(facet.AttributeFacet):
    __regid__ = 'subject-handedness-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Subject')
    order = 2
    rtype = 'handedness'
    title = _('Handedness')

class SubjectAgeFacet(facet.RangeFacet):
    __regid__ = 'subject-age-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Subject')
    path = ['X concerned_by S', 'S age_of_subject A']
    order = 3
    filter_variable = 'A'
    title = _('Age')

class SubjectStudyFacet(facet.RelationFacet):
    __regid__ = 'subject-study-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Subject')
    order = 4
    rtype = 'related_studies'
    target_attr = 'name'
    title = _('Studies')


def registration_callback(vreg):
    # Unregister unused/time-consuming facets
    from cubicweb.web.views.facets import (CWSourceFacet, CreatedByFacet,
                                           HasTextFacet, InGroupFacet, InStateFacet)
    vreg.unregister(CWSourceFacet)
    vreg.unregister(CreatedByFacet)
    vreg.unregister(InGroupFacet)
    vreg.unregister(InStateFacet)
    vreg.unregister(HasTextFacet)
    # Register medical exp
    vreg.register(SubjectGenderFacet)
    vreg.register(SubjectHandednessFacet)
    vreg.register(SubjectAgeFacet)
    vreg.register(SubjectStudyFacet)
