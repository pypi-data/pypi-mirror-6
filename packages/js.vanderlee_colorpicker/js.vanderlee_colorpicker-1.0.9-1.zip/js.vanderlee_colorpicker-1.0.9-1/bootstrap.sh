#!/bin/sh
virtualenv .
bin/pip install --ignore-installed setuptools==2.2
bin/pip install --no-dependencies zc.buildout==2.2.1
bin/buildout
