#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from mobilizon import Mobilizon, MobilizonClient, MobilizonEvent

if __name__ == "__main__":
	import sys

	config = None
	with open('config.json') as json_file:
		config = json.load(json_file)

	operation = "status"
	identity = None
	main_identity = config["identity"]

	parser = argparse.ArgumentParser(prog="Mobilizon Tool")
	parser.add_argument('operation', default="status", choices=["status", "list", "deleteall", "deletepast", "deletedupes"])
	parser.add_argument('-i', '--identity', type=int)
	args = parser.parse_args()
	operation = args.operation
	identity = args.identity

	if identity is not None:
		print('Using identity', identity)

	client = MobilizonClient(config["endpoint"])
	client.login(config["email"], config["password"], identity)

	identities = client.identities()
	print ('Identities:')
	for id in identities:
		print(' - ', id['id'], id['preferredUsername'])
		if int(id['id']) == client.identity:
			client.preferred_username = id['preferredUsername']
	print('Preferred username:', client.preferred_username)
	print ('Memberships:', client.memberships())
	if operation == 'list' or operation == 'deleteall' or operation == 'deletepast' or operation == 'deletedupes':
		events = client.list_events()
		print ('Events:')
		for event in events:

			if operation == 'list':
				event.print_event()
			else:
				print(' - ', event.id, event.title, event.beginsOn)

			if operation == 'deleteall':
				print('Deleting event', client.delete_event(event.id))
			if operation == 'deletepast' and event.is_past():
				print('Deleting past event', client.delete_event(event.id))
			if operation == 'deletedupes':
				for event2 in events:
					if event.id != event2.id:
						if event.is_same_event_as(event2):
							print(event.title, 'has dupes!', event.beginsOn, event2.beginsOn)
							print('Deleting second event', client.delete_event(event2.id))
