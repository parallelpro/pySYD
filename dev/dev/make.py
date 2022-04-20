# SOURCE PACKAGE ---> DEVELOPMENT BRANCH
import os
scripts = ['cli', 'models', 'pipeline', 'plots', 'target', 'utils']
rows = 18
rows_cli = 32

_ROOT, _ = os.path.split(os.path.abspath(os.getcwd()))
package = os.path.join(os.path.split(_ROOT)[0], 'pysyd')

# copy scripts from src -> dev 
for script in scripts:
    if script == 'cli':
        n = rows_cli
    else:
        n = rows
    # keep header of local script
    with open(os.path.join(_ROOT, "%s.py"%script), "r") as f:
        lines = [line for line in f.readlines()]
    header = lines[:n]
    # copy new body from pysyd package
    with open(os.path.join(package, '%s.py'%script), "r") as f:
        lines = [line for line in f.readlines()]
    body = lines[n:]
    # smash together header & body
    lines = header+body
    with open(os.path.join(_ROOT, "%s.py"%script), "w") as f:
        for line in lines:
            f.write(line)

import shutil 
# version is different
src = os.path.join(package, 'version.py')
dst = os.path.join(_ROOT, 'version.py')
shutil.copy(src, dst)

import glob
# make sure data and dicts are up-to-date
files = glob.glob(os.path.join(package, 'data', '*'))
for file in files:
    dst = os.path.join(_ROOT, 'info', 'data', file)
    shutil.copy(file, dst)
files = glob.glob(os.path.join(package, 'dicts', '*'))
for file in files:
    dst = os.path.join(_ROOT, 'dicts', file)
    shutil.copy(file, dst)