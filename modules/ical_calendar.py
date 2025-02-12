#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Import events from ical calendar
# STILL WIP

from modules.importmodule import ImportModule
from mobilizon import MobilizonEvent
import requests
from datetime import datetime, timedelta
import pytz
import json
import urllib.request
from ics import Calendar

class IcalCalendar(ImportModule):
    def name(self):
        return "ical_calendar"

    def get_events(self):
        events = []
        now = datetime.now(pytz.utc)
        c = Calendar(requests.get(self.config['ics_url']).text)
        for e in c.timeline.start_after(now):
            beginsOn = e.begin
            endsOn = e.end
            description = ""            
            if e.description:
                description = e.description

            location = ""
            if e.location:
                 location = e.location
            physicalAddress = { "description": location, "country": "Finland" }
            participation_url = ""
            if 'participation_url' in self.config:
                 participation_url = self.config['participation_url']
            image_url = ""
            if 'image_url' in self.config:
                 image_url = self.config['image_url']
            options = { "showRemainingAttendeeCapacity": False, "isOnline": False, "maximumAttendeeCapacity": 0, "remainingAttendeeCapacity": 0 }

            me = MobilizonEvent(title=e.name, beginsOn=beginsOn, endsOn=endsOn, description=description, onlineAddress=participation_url, externalParticipationUrl=participation_url, visibility="PUBLIC", physicalAddress=physicalAddress, options=options, joinOptions="EXTERNAL")
            events.append(me)
        return events

if __name__ == "__main__":
	te = IcalCalendar()
	te.get_events()
