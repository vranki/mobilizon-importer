#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from modules.demopartynet import DemopartyNet
from modules.tampere_events import TampereEvents
from modules.ical_calendar import IcalCalendar
from mobilizon import MobilizonEvent, MobilizonClient
import argparse

# Compare two dicts
def dict_differs(d1, d2):
	for k1, v1 in d1.items():
		val1 = v1
		if not val1:
			val1 = ""
		try:
			val2 = d2[k1]
			if not val2:
				val2 = ""
			if val1 != val2:
	#			print('Dicts differ', k1, v1, 'but in second', k1, d2[k1])
				return True
		except KeyError:
			if len(val1) > 0:
				return True
#	print('Dicts are equal', d1, d2)
	return False

def events_differ(old, new):
	old = old.get_dict();
	new = new.get_dict();

	ignore_keys = [ 'id', 'description', 'beginsOn', 'endsOn' ]

	for key in new.keys():
		if key not in ignore_keys:
			if isinstance(old.get(key), dict):
				if dict_differs(old.get(key), new.get(key)):
					return True
			else:
				if old.get(key) != new.get(key):
					print('Key', key, 'differs:', old.get(key), ' -> ', new.get(key))
					return True
	return False

def handle_events(new_events, existing_events, limit):
	handled_events = 0
	if limit == 0:
		limit = 99999999
	for event in new_events:
		if event.is_past():
			print('Ignoring passed event', event.title, 'which was', event.beginsOn)
		else:
			this_existing_event = None
			for existing_event in existing_events:
				if event.is_same_event_as(existing_event):
					this_existing_event = existing_event
			if this_existing_event:
				print('Event already exists:', this_existing_event.id, this_existing_event.title)
				changed = events_differ(this_existing_event, event)
				if changed:
					print('Event data has changed, need to update it!')
					event.id = this_existing_event.id
					r = client.update_event(event)
					print('Updated', r)
					handled_events = handled_events + 1			
			else:
				print('New event:', event.title, event.beginsOn)
				client.create_event_from_dict(event.get_dict())
				handled_events = handled_events + 1
		if handled_events >= limit:
			print('Reached limit of', limit, 'events, stopping..')
			break

if __name__ == "__main__":
	config = None
	with open('config.json') as json_file:
		config = json.load(json_file)

	client = MobilizonClient(config["endpoint"])

	modules = []

	for module in config['modules']:
		print('Module', module)
		if module['module'] == 'demopartynet':
			modules.append(DemopartyNet(module))
		if module['module'] == 'tampere_events':
			modules.append(TampereEvents(module))
		if module['module'] == 'ical_calendar':
			modules.append(IcalCalendar(module))

	parser = argparse.ArgumentParser(prog="Mobilizon Importer")
	parser.add_argument('-t', '--test', type=str)
	parser.add_argument('-l', '--limit', type=int, default=0)
	args = parser.parse_args()

	for module in modules:
		if not module.enabled:
			continue
		identity = module.get_identity()
		attributed_to = module.get_attributedto()
		print('Handling module', module.name(), 'as', identity, 'attributed to', attributed_to, '..')
		client.login(config["email"], config["password"], identity, attributed_to)

		events = module.get_events()

		if args.test == 'list_module':
			for event in events:
				event.print_event()
		else:
			existing_events = client.list_events()
			if args.test == 'list_mobilizon':
				for event in existing_events:
					# event.print_event()
					print(event.get_dict())
				continue

			if not config['dry_run']:
				handle_events(events, existing_events, args.limit)
