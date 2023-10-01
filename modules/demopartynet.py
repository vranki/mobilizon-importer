#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Import events from demoparty.net
#

from modules.importmodule import ImportModule, MobilizonEvent
import requests
from datetime import datetime
import json
import feedparser

class DemopartyNet(ImportModule):
	def name(self):
			return "demopartynet"

	def get_events(self):
		events = []
		feed = feedparser.parse('https://www.demoparty.net/demoparties.xml')
		for entry in feed.entries:
			description = entry.summary[entry.summary.index('</dl>') + 5:-1]
			description = description.strip()
			thumbnail = None
			try:
				thumbnail = entry.media_thumbnail[0]["url"]
			except:
				pass
			# In format Fri, 18 Nov 2022 00:00:00 +0100
			dateformat = '%a, %d %b %Y %H:%M:%S %z'
			beginsOn = datetime.strptime(entry.demopartynet_startdate, dateformat)
			endsOn = datetime.strptime(entry.demopartynet_enddate, dateformat)
			print(entry.id, entry.title, entry.link)
			me = MobilizonEvent(title=entry.title, beginsOn=beginsOn, endsOn=endsOn, description=description, onlineAddress=entry.link, category="PARTY", visibility="PUBLIC")
			# , picture=thumbnail , physicalAddress=entry.demopartynet_country (don't work yet)
			events.append(me)
		return events

if __name__ == "__main__":
	dpn = DemopartyNet()
	dpn.get_events()
