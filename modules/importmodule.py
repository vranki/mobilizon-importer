#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class ImportModule(ABC):
	def __init__(self, config=None):
		self.maxduration = 999999
		self.maxfuture = 9999999
		self.attributed_to = None
		if config:
			self.config = config
			self.enabled = self.config['enabled']
			if 'maxduration' in self.config:
				self.maxduration = self.config['maxduration']
			if 'maxfuture' in self.config:
				self.maxfuture = self.config['maxfuture']
			if 'attributedto' in self.config:
				self.attributed_to = self.config['attributedto']
		else:
			self.config = None
			self.enabled = True
    
	@abstractmethod
	def get_events(self):
		pass

	@abstractmethod
	def name(self):
		return None

	def get_identity(self):
		if self.config:
			return int(self.config['identity'])
		return 0

	def get_attributedto(self):
		if self.attributed_to:
			return self.attributed_to
		return self.get_identity
