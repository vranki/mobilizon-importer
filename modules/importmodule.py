#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class MobilizonEvent:
	def __init__(self, title, beginsOn, endsOn=None, description="", actor_id=None, status="CONFIRMED", visibility="PRIVATE", joinOptions=None, draft=False, tags=None, picture=None, onlineAddress=None, phoneAddress=None, category=None, physicalAddress=None, options=None, contacts=None, id=None):

		if not endsOn:
			endsOn = beginsOn
		self.id = id
		self.title = title
		self.beginsOn = beginsOn
		self.endsOn = endsOn
		self.description = description
		self.actor_id = actor_id
		self.status=status
		self.visibility=visibility
		self.joinOptions=joinOptions
		self.draft=draft
		self.tags=tags
		self.picture=picture
		self.onlineAddress=onlineAddress
		self.phoneAddress=phoneAddress
		self.category=category
		self.physicalAddress=physicalAddress
		self.options=options
		self.contacts=contacts

	def get_dict(self):
		variables = {
			"id": self.id, 
			"title": self.title, 
			"description": self.description,
			"beginsOn": self.beginsOn,
			"endsOn": self.endsOn,
			"status": self.status, # CANCELLED / CONFIRMED / TENTATIVE
			"visibility": self.visibility, # PRIVATE, PUBLIC, RESTRICTED, UNLISTED
			"joinOptions": self.joinOptions,
			"draft": self.draft,
			"tags": self.tags,
			"picture": self.picture,
			"onlineAddress": self.onlineAddress,
			"phoneAddress": self.phoneAddress,
			"category": self.category,
			"physicalAddress": self.physicalAddress,
			"options": self.options,
			"contacts": self.contacts
		}
		filtered_variables = {k: v for k, v in variables.items() if v is not None}
		return filtered_variables
	@staticmethod
	def from_dict(d):
		return MobilizonEvent(d.get('title'), d.get('beginsOn'), d.get('endsOn'), d.get('description'), d.get('actor_id'), d.get('status'), d.get('visibility'), d.get('joinOptions'), d.get('draft'), d.get('tags'), d.get('picture'), d.get('onlineAddress'), d.get('phoneAddress'), d.get('category'), d.get('physicalAddress'), d.get('options'), d.get('contacts'), d.get('id'))

class ImportModule(ABC):
    def __init__(self, modules_config):
    	self.enabled = modules_config[self.name()]['enabled']
    
    @abstractmethod
    def get_events(self):
    	pass

    @abstractmethod
    def name(self):
    	return None
   

