"""Root conftest.py - loads framework fixtures for all tests."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.fixtures import *
