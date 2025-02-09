#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Import events from tapahtumat.tampere.fi
#
# STILL WIP

from modules.importmodule import ImportModule
from mobilizon import MobilizonEvent
import requests
from datetime import datetime, timedelta
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
				continue
			if entry['pageType'] != 'event':
				continue
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
				continue
			try:
				endsOn = datetime.strptime(entry['defaultEndDate'], format)
				endsOn.replace(tzinfo=pytz.UTC)
				endsOn = endsOn.replace(tzinfo=pytz.UTC).astimezone(tz=None)
			except KeyError:
				print('No end for', entry)
				continue
			
			if endsOn - beginsOn > timedelta(hours=self.maxduration):
				print(f'Event {title} duration too long', endsOn - beginsOn)
				continue

			utc=pytz.UTC
			now = datetime.now()
			now = utc.localize(now)

			if beginsOn - now > timedelta(hours=self.maxfuture):
				print(f'Event {title} too far in future', beginsOn)
				continue


			imageId = entry['imageDesktop']
			imageUrl = f'https://s3.eu-central-1.amazonaws.com/eventz.today.prod/images/{imageId}'
			url = f'https://tapahtumat.tampere.fi/fi-FI/page/{id}'

			if 'hashtags' in entry:
				tagstring = "\n\n"
				for tag in entry['hashtags']:
					tagstring = tagstring + "#" + tag + " "

				description = description + tagstring

			physicalAddress = None
			if len(entry['locations']) > 0:
				location = entry['locations'][0]['address']

				#print(entry)
				# print(id, title, description, beginsOn, endsOn, url, location)
				# print('"""""""""""""')
				''' 
				physicalAddress: {
					description: "Somewhere",
					street: "",
					locality: "",
					region: "",
					country: "",
					type: "",
					postalCode: "",
				},
				'''				
				desc = entry['locations'][0]['address']
				street = ""
				locality = ""
				region = ""
				type = ""
				postalCode = ""
				geom = f"{entry['locations'][0]['lng']};{entry['locations'][0]['lat']}"
				physicalAddress = { "description": desc, "geom": geom, "country": "Finland", "postalCode": postalCode, "locality": locality, "street": street }
			
			options = { "showRemainingAttendeeCapacity": False, "isOnline": False, "maximumAttendeeCapacity": 0, "remainingAttendeeCapacity": 0 }
			me = MobilizonEvent(title=title, beginsOn=beginsOn, endsOn=endsOn, description=description, onlineAddress=url, externalParticipationUrl=url, visibility="PUBLIC", physicalAddress=physicalAddress, options=options, joinOptions="EXTERNAL")
			'''
			  			picture: {
    			id: "",
    			name: "",
    			alt: "",
    			metadata: {},
    			url: "https://mobilizon.fr/media/81d9c76aaf740f84eefb28cf2b9988bdd2495ab1f3246159fd688e242155cb23.png?name=Screenshot_20220315_171848.png",
  			},
			'''
			events.append(me)

		return events

if __name__ == "__main__":
	te = TampereEvents()
	te.get_events()
