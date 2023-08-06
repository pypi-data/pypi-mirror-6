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

"""cubicweb-neuroimaging views/forms/actions/components for web ui"""
from cubicweb.view import EntityView
from cubicweb.selectors import is_instance


class MRIDataOutOfContextView(EntityView):
    __regid__ = 'scan-data-view'
    __select__ = EntityView.__select__ & is_instance('MRIData')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        if entity.sequence:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Sequence'), entity.sequence))
        if entity.shape_x:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Image Shape (x)'), entity.shape_x))
        if entity.shape_y:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Image Shape (y)'), entity.shape_y))
        if entity.shape_z:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Image Shape (z)'), entity.shape_z))
        if entity.shape_t:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Image Shape (t)'), entity.shape_t))
        if entity.voxel_res_x:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Voxel resolution (x)'), entity.voxel_res_x))
        if entity.voxel_res_y:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Voxel resolution (y)'), entity.voxel_res_y))
        if entity.voxel_res_z:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Voxel resolution (z)'), entity.voxel_res_z))
        if entity.fov_x:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Fov (x)'), entity.fov_x))
        if entity.fov_y:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Fov (y)'), entity.fov_y))
        if entity.tr:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Tr'), entity.tr))
        if entity.te:
            self.w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._('Te'), entity.te))
