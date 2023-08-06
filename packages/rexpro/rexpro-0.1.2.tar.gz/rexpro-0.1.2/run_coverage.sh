#!/bin/bash

mkdir ./coverage &>/dev/null
nosetests --attr=unit --with-coverage --cover-erase --cover-package=rexpro --cover-html --cover-xml --cover-min-percentage=95 --cover-html-dir=./coverage/ --cover-xml-file=./coverage/coverage.xml
