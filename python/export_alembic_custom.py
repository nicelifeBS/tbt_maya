#!/usr/bin/env python

import sys
import os

import tbt_utils

import maya.standalone
maya.standalone.initialize('Python')

scene = sys.argv[1]
proj_dir = sys.argv[2]

if os.path.exists(scene):
    tbt_utils.write_alembic(scene, proj_dir)
else:
    print 'File {} does not exist'.format(scene)