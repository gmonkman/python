from __future__ import print_function
from nose.tools import *
import NAME

def setup():
	print("SETUP!")

def teardown():
	print("TEAR DOWN!")

def test_basic():
  print("I RAN!")