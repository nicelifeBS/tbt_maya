#!/usr/bin/env python

"""
Custom alembic export script for the fullbody shots of the horse. Change the
variables scene and project to the file you want to export. And then run the
script from the commandline:

    python export_alembix_custom.py

This script should be run with mayapy runtime. For this you can use the 
write_alembic_custom runner script:

    python write_alembic_custom
"""

import sys
import os

import tbt_utils

import maya.standalone

maya.standalone.initialize('Python')

import pymel.core as pm

def export_alembic_bake(start, stop, options, suffix=''):
    path = pm.workspace.getPath().joinpath(pm.workspace.fileRules['alembicCache'])
    path = path.joinpath(pm.sceneName().basename().splitext()[0] + suffix + '.abc')
    print 'export to: ', path
    print 'start frame: ', start
    print 'end frame: ', stop
    opt = '-frameRange {start} {stop} -noNormals -dataFormat ogawa {options} -file \"{path}\"'
    print 'alembic options: ', opt.format(
        start=start, stop=stop, options=options, path=path
    )
    pm.AbcExport(j=opt.format(start=start, stop=stop, options=options, path=path))


def write_alembic(nodes):
    """Export given nodes as alembic abc file. Start and end frame are looked up
    by querying the playback options
    Args:
        nodes (list): list of node locations
    """
    start = pm.playbackOptions(ast=True, query=True)
    end = pm.playbackOptions(aet=True, query=True)

    option_str = []
    if nodes:
        for node in nodes:
            print 'node: ', node
            option_str.append('-root |{}'.format(node.longName()))

        export_alembic_bake(start, end, ' '.join(option_str))
    else:
        raise IOError('Nodes not found')

# scene file and project to load
#scene = '/Users/bjoern_siegert/Dropbox (Snowgum Films)/Share/Horse/Rendering_FullBodyHorse/scenes/TB_01130/TB_01130_AnimateHorse_v03_bsi.mb'
project = '/Users/bjoern_siegert/Dropbox (Snowgum Films)/Share/Horse/Rendering_FullBodyHorse'

scene = sys.argv[1]

print 'Trying to load scene:\n{}'.format(scene)

if not os.path.exists(scene):
    raise IOError('File {} does not exist'.format(scene))
else:

    import glob
    import os

    print 'Loading abc plugin'
    pm.loadPlugin('AbcExport.bundle')

    print 'Setting project to: ', project
    pm.workspace.open(project)
    # open the file
    pm.openFile(scene, open=True, force=True)

    search = [
        '*:Horse_Rig_MasterRig_v01:groom_rigged',
        '*:Horse_Rig_MasterRig_v01:Grp_Mesh'
    ]

    nodes = []
    for s in search:
        nodes.extend(pm.ls(s))
    write_alembic(nodes)

