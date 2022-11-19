#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from mobilizon import MobilizonClient
from modules.demopartynet import DemopartyNet

if __name__ == "__main__":
	config = None
	with open('config.json') as json_file:
	    config = json.load(json_file)
	print(config)

	client = MobilizonClient(config["endpoint"])
	client.login(config["email"], config["password"], config["identity"])

	dpn = DemopartyNet()
	events = dpn.get_events()

	for event in events:
		print(event.get_dict())
		client.create_event_from_dict(event.get_dict())

	print('Found', len(events), 'events')
	exit(0)
	print ('Identities:', client.identities())
	print ('Memberships:', client.memberships())


