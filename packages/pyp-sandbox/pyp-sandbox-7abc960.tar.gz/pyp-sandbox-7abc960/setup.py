import argparse
import os
import sys

from setuptools import setup



if __name__ == '__main__':

    if not any(k in sys.argv[1:] for k in ('--help', '--help-commands')):
        #parser = argparse.ArgumentParser(description="Satori installation options.")
        #parser.add_argument("--minimal", action="store_true", help=MINIMAL)
        #config, unknown = parser.parse_known_args()
        #if config.minimal:
        install = sys.argv[1] in ('install', 'develop')
        if not install or (install and '--minimal' in sys.argv[1:]):
            print "[ %s ] SETTING PBR_REQUIREMENTS_FILES to minimal-requirements.txt" % sys.argv[1]
            os.environ['PBR_REQUIREMENTS_FILES'] = 'minimal-requirements.txt'
            if install:
                sys.argv.remove('--minimal')

    setup(
        setup_requires=['pbr-samstav'],
        pbr=True)

    os.environ['PBR_REQUIREMENTS_FILES'] = ''

