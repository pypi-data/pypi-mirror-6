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

"""cubicweb-neuroimaging entity's classes"""
import os.path as osp

from cubicweb.entities import AnyEntity, fetch_config


class Scan(AnyEntity):
    __regid__ = 'Scan'
    fetch_attrs, fetch_order = fetch_config(('type', 'label', 'format', 'description'))

    def dc_title(self):
        return u'%s (%s)' % (self._cw._('Scan'), self.type)

    @property
    def image_url(self):
        if self.type in ('normalized T1', 'raw T1'):
            return self._cw.data_url('anat.jpg')
        elif self.type == 'c map':
            return self._cw.data_url('c_map.jpg')
        elif self.type == 't map':
            return self._cw.data_url('t_map.jpg')
        elif self.type in ('preprocessed fMRI', 'raw fMRI'):
            return self._cw.data_url('fmri.jpg')
        elif self.type == 'dti':
            return self._cw.data_url('dti.jpg')
        elif self.type == 'boolean mask':
            return self._cw.data_url('mask.jpg')
