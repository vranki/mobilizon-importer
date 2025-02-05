#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from mobilizon import MobilizonClient
from modules.demopartynet import DemopartyNet
from modules.tampere_events import TampereEvents
from mobilizon import is_same_event

def events_differ(old, new):
	old = old.get_dict();
	new = new.get_dict();

	ignore_keys = [ 'id', 'description', 'beginsOn', 'endsOn' ]

	for key in new.keys():
		if key not in ignore_keys:
			if old.get(key) != new.get(key):
				print('Key', key, 'differs:', old.get(key), ' -> ', new.get(key))
				return True
	return False

def handle_events(new_events, existing_events):
	for event in new_events:
		if event.is_past():
			print('Ignoring passed event', event.title, 'which was', event.beginsOn)
		else:
			event.joinOptions = "FREE" # Set for all imported
			this_existing_event = None
			for existing_event in existing_events:
				if is_same_event(event, existing_event):
					this_existing_event = existing_event
			if this_existing_event:
				print('Event already exists:', this_existing_event.id, this_existing_event.title)
				changed = events_differ(this_existing_event, event)
				if changed:
					print('Event data has changed, need to update it!')
					event.id = this_existing_event.id
					r = client.update_event(event)
					print('Updated', r)
				
			else:
				print('New event:', event.title, event.beginsOn)
				client.create_event_from_dict(event.get_dict())

if __name__ == "__main__":
	config = None
	with open('config.json') as json_file:
		config = json.load(json_file)

	client = MobilizonClient(config["endpoint"])

	dpn = DemopartyNet(config['modules'])
	te = TampereEvents(config['modules'])

	modules = []
	if dpn.enabled:
		modules.append(dpn)
	if te.enabled:
		modules.append(te)

	for module in modules:
		identity = module.get_identity()
		print('Handling module', module.name(), 'as', identity, '..')
		client.login(config["email"], config["password"], identity)
		existing_events = client.list_events()
		events = module.get_events()
		if not config['dry_run']:
			handle_events(events, existing_events)
