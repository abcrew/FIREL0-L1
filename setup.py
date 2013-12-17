from distutils.core import setup

setup(name='FIREBIRD',
      version='1.0',
      packages=['DataSync', 'L0toL1', 'L1toL2', 'SciRequest'],
      scripts=['scripts/FIRE_L0_L1.py', 'scripts/makeRequest.py']
      )
