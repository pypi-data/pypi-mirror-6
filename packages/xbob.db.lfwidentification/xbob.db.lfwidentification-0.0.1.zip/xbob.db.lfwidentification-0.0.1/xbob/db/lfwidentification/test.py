#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2013-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the LFW Identification database.
"""

import os, sys
import unittest
import xbob.db.lfwidentification

class LFWIdentificationDatabaseTest(unittest.TestCase):
  """Performs various tests on the LFW Identification database."""

  def test01_clients(self):
    # test that the clients() function returns reasonable output
    db = xbob.db.lfwidentification.Database()

    self.assertEqual(len(db.clients(protocol='P0')), 1680)
    self.assertEqual(len(db.clients(protocol='P0', groups='world')), 280)
    self.assertEqual(len(db.clients(protocol='P0', groups='dev')), 400)
    self.assertEqual(len(db.clients(protocol='P0', groups='eval')), 1000)

  def test02_objects(self):
    # test that the objects() function returns reasonable output
    db = xbob.db.lfwidentification.Database()

    self.assertEqual(len(db.objects(protocol='P0')), 9164)
    self.assertEqual(len(db.objects(protocol='P0', groups='world')), 4613)
    self.assertEqual(len(db.objects(protocol='P0', groups='dev')), 1254)
    self.assertEqual(len(db.objects(protocol='P0', groups='eval')), 3297)
    self.assertEqual(len(db.objects(protocol='P0', groups='dev', purposes='enrol')), 400)
    self.assertEqual(len(db.objects(protocol='P0', groups='dev', purposes='probe')), 854)
    self.assertEqual(len(db.objects(protocol='P0', groups='eval', purposes='enrol')), 1000)
    self.assertEqual(len(db.objects(protocol='P0', groups='eval', purposes='probe')), 2297)

  def test03_object_sets(self):
    # test that the object_probesets() function returns reasonable output
    db = xbob.db.lfwidentification.Database()

    self.assertEqual(len(db.object_sets(protocol='P0', groups=('dev','eval'), purposes='probe')), 0)
    self.assertEqual(len(db.object_sets(protocol='P0', groups='dev', purposes='probe')), 0)
    self.assertEqual(len(db.object_sets(protocol='P0', groups='eval', purposes='probe')), 0)
    self.assertEqual(len(db.object_sets(protocol='P0set', groups=('dev','eval'), purposes='probe')), 1400)
    self.assertEqual(len(db.object_sets(protocol='P0set', groups='dev', purposes='probe')), 400)
    self.assertEqual(len(db.object_sets(protocol='P0set', groups='eval', purposes='probe')), 1000)

  def test04_driver_api(self):

    from bob.db.script.dbmanage import main

    self.assertEqual(main('lfwidentification dumplist --self-test'.split()), 0)
    self.assertEqual(main('lfwidentification dumplist --protocol=P0 --class=client --group=dev --purpose=enrol --self-test'.split()), 0)
    self.assertEqual(main('lfwidentification checkfiles --self-test'.split()), 0)

