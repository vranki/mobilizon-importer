#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class ImportModule(ABC):
	def __init__(self, modules_config=None):
		if modules_config:
			self.config = modules_config[self.name()]
			self.enabled = modules_config[self.name()]['enabled']
			self.maxduration = modules_config[self.name()]['maxduration']
			self.maxfuture = modules_config[self.name()]['maxfuture']
		else:
			self.config = None
			self.enabled = True
			self.maxduration = 999999
			self.maxfuture = 9999999
    
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
