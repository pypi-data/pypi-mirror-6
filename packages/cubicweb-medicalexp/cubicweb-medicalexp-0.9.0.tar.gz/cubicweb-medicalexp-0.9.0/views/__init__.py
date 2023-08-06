# -*- coding: utf-8 -*-
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

from cubicweb.web import views

# Monkey patch for having list of one element after facets
# rather than the primary view
def vid_from_rset(req, rset, schema):
    """given a result set, return a view id"""
    if rset is None:
        return 'index'
    for mimetype in req.parse_accept_header('Accept'):
        if mimetype in VID_BY_MIMETYPE:
            return VID_BY_MIMETYPE[mimetype]
    nb_rows = rset.rowcount
    # empty resultset
    if nb_rows == 0:
        return 'noresult'
    # entity result set
    if not schema.eschema(rset.description[0][0]).final:
        if need_table_view(rset, schema):
            return 'table'
        if nb_rows == 1:
            if req.form.get('_facet', None):
                if len(rset.column_types(0)) == 1:
                    return 'sameetypelist'
                else:
                    return 'list'
            elif req.search_state[0] == 'normal':
                return 'primary'
            else:
                return 'outofcontext-search'
        if len(rset.column_types(0)) == 1:
            return 'sameetypelist'
        return 'list'
    return 'table'


views.vid_from_rset = vid_from_rset
