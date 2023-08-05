#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
"""
  paths.__init__.py

  Python utility module for dealing with local paths

  :copyright: Copyright (C) 2013 Nik Cubrilovic and others, see AUTHORS
  :license: MIT, see LICENSE for more details.
"""

class path(object):

	def __init__(self, initial=None):
		self.normalize(initial)
		# if not os.path.exists()


