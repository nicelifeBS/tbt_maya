import pymel.core as pm
import shutil
import os

w=pm.workspace
root = w.path
source_images = w.fileRules['sourceImages']
new_path = os.path.join(root, source_images)
for f in pm.ls(type='file'):
    to_copy = f.fileTextureName.get()
    copy_path = os.path.join(new_path, os.path.basename(to_copy))
    shutil.copy2(to_copy, copy_path)
