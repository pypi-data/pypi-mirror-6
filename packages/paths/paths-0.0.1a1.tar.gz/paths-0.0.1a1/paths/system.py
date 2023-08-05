#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
"""
  paths.system.py

  Python utility module for dealing with local paths

  :copyright: Copyright (C) 2013 Nik Cubrilovic and others, see AUTHORS
  :license: MIT, see LICENSE for more details.
"""

import os
import sys

def _darwin_user_data_dir(name):
	"""Will create a user data directory and return the path as a string.
	"""
	pass

def _darwin_sys_data_dir(name):
	"""Will create a user data directory and return the path as a string.
	"""
	pass

def _win_user_data_dir(name):
	"""Will create a user data directory and return the path as a string.

	http://ss64.com/nt/syntax-variables.html
	http://support.microsoft.com/default.aspx?scid=kb;en-us;310294
	"""
	pass

def _win_sys_data_dir(name):
	"""Will create a user data directory and return the path as a string.
	"""
	pass

def _posix_user_data_dir(name):
	"""Will create a user data directory and return the path as a string.
	"""
	pass

def _posix_sys_data_dir(name):
	"""Will create a user data directory and return the path as a string.
	"""
	pass

def sys_data_dir():
	pass

def system_config_path():
	pass


if sys.platform == 'darwin':
	user_data_dir = _darwin_user_data_dir
	sys_data_dir = _darwin_sys_data_dir
elif sys.platform.startswith('win'):
	user_data_dir = _win_user_data_dir
	sys_data_dir = _win_sys_data_dir
else:
	user_data_dir = _posix_user_data_dir
	sys_data_dir = _posix_sys_data_dir
