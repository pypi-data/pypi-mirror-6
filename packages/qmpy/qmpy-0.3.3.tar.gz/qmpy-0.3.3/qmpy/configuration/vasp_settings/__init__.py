import yaml
import os, os.path
from qmpy import INSTALL_PATH

vs_path = os.path.dirname(os.path.abspath(__file__))

thubbards = yaml.load(open(vs_path+'/hubbards.yml').read())
hubbards = {}
for setting, data in thubbards.items():
    hubbards[setting] = {}
    for k, v in data.items():
        elt, lig, ox = k.split('_')
        if ox == '*':
            hubbards[setting][(elt, lig, None)] = v
        else:
            hubbards[setting][(elt, lig, float(ox))] = v

HUBBARDS = hubbards
POTENTIALS = yaml.load(open(vs_path+'/potentials.yml').read())

VASP_SETTINGS = {}
for f in os.listdir(vs_path+'/inputs/'):
    settings =  yaml.load(open('%s/inputs/%s' % (vs_path, f)).read())
    VASP_SETTINGS[f.replace('.yml','')] = settings
