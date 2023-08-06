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

"""cubicweb-neuroimaging schema"""

from yams.buildobjs import (EntityType, SubjectRelation, String, RichString,
                            Int, Float, Boolean, Bytes)

SCAN_DATA = ('PETData', 'MRIData', 'DMRIData')

### IMAGE AND SCAN ############################################################
class Scan(EntityType):
    label = String(maxsize=256, required=True, indexed=True, fulltextindexed=True)
    type = String(maxsize=256, required=True, indexed=True)
    format = String(maxsize=128, indexed=True)
    has_data = SubjectRelation(SCAN_DATA, cardinality='?1', inlined=True, composite='subject')
    completed = Boolean(indexed=True)
    valid = Boolean(indexed=True)
    description = RichString(fulltextindexed=True)
    # We use position here, as it may be useful for processed scans
    # Position of acquisition during session
    position_acquisition = Int(indexed=True)
    related_regions = SubjectRelation('AnatomicalRegion', cardinality='**')


class AnatomicalRegion(EntityType):
    name = String(maxsize=256, indexed=True)
    region_id = String(maxsize=256, indexed=True)
    ## hemisphere = String(vocabulary=('right', 'left'), indexed=True)
    hemisphere = String(indexed=True)
    uri = String(maxsize=256, indexed=True)


class PETData(EntityType):
    # Image technical information
    voxel_res_x = Float(required=True, indexed=True)
    voxel_res_y = Float(required=True, indexed=True)
    voxel_res_z = Float(required=True, indexed=True)
    tr = Float(required=True, indexed=True)
    te = Float(required=True, indexed=True)


class MRIData(EntityType):
    sequence = String(maxsize=128, indexed=True)
    # Image technical information
    shape_x = Int(indexed=True)
    shape_y = Int(indexed=True)
    shape_z = Int(indexed=True)
    shape_t = Int(indexed=True)
    voxel_res_x = Float(indexed=True)
    voxel_res_y = Float(indexed=True)
    voxel_res_z = Float(indexed=True)
    # MRI specific. Should be put elsewhere ?
    fov_x = Float(indexed=True)
    fov_y = Float(indexed=True)
    tr = Float(indexed=True)
    te = Float(indexed=True)
    affine = Bytes()


class DMRIData(EntityType):
    # Image technical information
    voxel_res_x = Float(required=True, indexed=True)
    voxel_res_y = Float(required=True, indexed=True)
    voxel_res_z = Float(required=True, indexed=True)
    # MRI specific. Should be put elsewhere ?
    fov_x = Float(indexed=True)
    fov_y = Float(indexed=True)
    tr = Float(required=True, indexed=True)
    te = Float(required=True, indexed=True)
