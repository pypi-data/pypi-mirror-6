#!/bin/bash
VERSION=`python setup.py -V`
python setup.py --command-packages=stdeb.command debianize
debuild
rm -rfv subdownloaderlite.egg-info build
rm -rfv *.pyc
rm -rfv */*.pyc
rm -rfv */*/*.pyc
rm -rfv debian
