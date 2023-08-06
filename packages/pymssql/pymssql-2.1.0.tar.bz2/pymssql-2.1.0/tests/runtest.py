#!/usr/bin/env python

from os.path import abspath, dirname, join
import sys
sys.path.append(abspath(join(dirname(__file__), '..')))
# sys.path.append(abspath(dirname(__file__)))

import nose
from tests.nose_plugin import ConfigPlugin

if __name__ == '__main__':
    nose.main(addplugins=[ConfigPlugin()])
