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

""" Schema test """

from cubicweb.devtools.testlib import CubicWebTC

class NeuroimagingSchemaTC(CubicWebTC):
    """ Test proper behavior with respect to the composite relations. """
    def setup_database(self):
        """ Several entities involving composite relations are created,
            according to the schema.
        """
        req = self.request()
        t_scan = req.create_entity('Scan', label=u'TS1', type=u'test type')
        t_pet_data = req.create_entity('PETData', voxel_res_x=50., voxel_res_y=75.,
                                       voxel_res_z=45., tr=12.5, te=3.5,
                                       reverse_has_data=t_scan)

    def test_cleanup_on_scan_delete(self):
        """ Test that on Scan deletion, PETData, MRIData and DMRIData
            are deleted.
        """
        req = self.request()
        t_scan = req.execute('Any X WHERE X is Scan').get_entity(0, 0)
        db_t_pet = req.execute('Any X WHERE X is PETData')
        if not db_t_pet:
            self.fail('Scan data is missing from the database')
        req.execute('DELETE Scan X WHERE X eid %(scaneid)s', {'scaneid': t_scan.eid})
        self.commit()
        db_t_pet = req.execute('Any X WHERE X is PETData')
        if db_t_pet:
            self.fail('The scan data was not deleted.')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
