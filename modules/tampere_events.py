#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Import events from tapahtumat.tampere.fi
#
# STILL WIP

from modules.importmodule import ImportModule, MobilizonEvent
import requests
from datetime import datetime
import pytz
import json
import urllib.request

class TampereEvents(ImportModule):
	def name(self):
			return "tampere_events"

	def get_events(self):
		events = []
		data = None
		localtz = pytz.timezone('Europe/Helsinki')

		with urllib.request.urlopen("https://tapahtumat.tampere.fi/api/collection/634844c32f41a024ee51a234/content?lang=fi&country=FI&hashtagsForContentSelection=&mode=event&sort=startDate") as url:
			data = json.load(url)

		data = data['pages']

		for entry in data:
			if entry['privacy'] != 'public':
				break
			if entry['pageType'] != 'event':
				break
			id = entry['_id']
			title = entry['name']
			description = entry['descriptionLong']

			format = "%Y-%m-%dT%H:%M:%S.%fZ"
			try:
				beginsOn = datetime.strptime(entry['defaultStartDate'], format)
				beginsOn.replace(tzinfo=pytz.UTC)
				beginsOn = beginsOn.replace(tzinfo=pytz.UTC).astimezone(tz=None)
			except KeyError:
				print('No start for', entry)
				return
			try:
				endsOn = datetime.strptime(entry['defaultEndDate'], format)
				endsOn.replace(tzinfo=pytz.UTC)
				endsOn = endsOn.replace(tzinfo=pytz.UTC).astimezone(tz=None)
			except KeyError:
				print('No end for', entry)
				return
			imageId = entry['imageDesktop']
			imageUrl = f'https://s3.eu-central-1.amazonaws.com/eventz.today.prod/images/{imageId}'
			url = f'https://tapahtumat.tampere.fi/fi-FI/page/{id}'

			location = None # Default to virtual
			if len(entry['locations']) > 0:
				location = entry['locations'][0]['address']

			#print(entry)
			print(id, title, description, beginsOn, endsOn, url, location)
			print('"""""""""""""')

			description = description + f'\n\n{location}'

			if 'hashtags' in entry:
				tagstring = "\n\n"
				for tag in entry['hashtags']:
					tagstring = tagstring + "#" + tag + " "

				description = description + tagstring

			me = MobilizonEvent(title=title, beginsOn=beginsOn, endsOn=endsOn, description=description, onlineAddress=url, visibility="PUBLIC")
			# PhysicalAddress is AddressInput, no clue how to set it
			# , picture=thumbnail , physicalAddress=location (don't work yet)
			events.append(me)

		return events

if __name__ == "__main__":
	te = TampereEvents()
	te.get_events()
