#!/bin/bash

export PATH=\
/opt/buildout.python/bin:\
$PATH:

if [[ "$1" = "plone-4.0" ]]
then
    python_version=2.6
    config=test-4.0.x.cfg
fi

if [[ "$1" = "plone-4.1" ]]
then
    python_version=2.6
    config=test-4.1.x.cfg
fi

if [[ "$1" = "plone-4.2" ]]
then
    python_version=2.6
    config=test-4.2.x.cfg
fi

if [[ "$1" = "plone-4.3" ]]
then
    python_version=2.7
    config=test-4.3.x.cfg
fi

virtualenv-$python_version .
bin/python bootstrap.py -c $config
bin/buildout -c $config
bin/test vs.contentnavigation
