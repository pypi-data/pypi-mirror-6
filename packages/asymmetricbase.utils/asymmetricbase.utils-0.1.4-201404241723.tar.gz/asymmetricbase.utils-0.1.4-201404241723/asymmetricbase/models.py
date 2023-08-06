# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import models

from asymmetricbase.fields.textfields import LongNameField

class AbstractBaseAddress(models.Model):
	class Meta(object):
		abstract = True
	
	name = LongNameField(default = "", blank = True) # For easier searching
	
	# Standard contact detail
	address_line_1 = models.CharField("Address", max_length = 255, default = "", blank = True)
	address_line_2 = models.CharField(max_length = 255, default = "", blank = True)
	city = models.CharField(max_length = 30, default = "", blank = True)
	province = models.CharField(max_length = 50, default = "", blank = True)
	postal_code = models.CharField(max_length = 10, default = "", blank = True)
	country = models.CharField(max_length = 25, default = "", blank = True)
	phone = models.CharField(max_length = 25, default = "", blank = True)
	fax = models.CharField(max_length = 25, default = "", blank = True)
	
	
	def __str__(self):
		return "{self.name}, {self.address_line_1}, {self.city}, {self.province}, {self.postal_code}".format(self = self)
	
	@property
	def address_summary(self):
		return u'{self.address_line_1}, {self.city}, {self.postal_code}'.format(self = self)
