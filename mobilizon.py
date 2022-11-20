#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Based on snipped by setol at https://framagit.org/-/snippets/6640 - thanks!
#
# use `pip install gql tenacity`

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from requests.exceptions import HTTPError
from tenacity import *
from datetime import datetime
import json
import pytz
from enum import Enum
from modules.importmodule import MobilizonEvent

# this class has been integrated in Tenacity after 7.0.0 release
# see https://github.com/jd/tenacity/blame/c18dcfbf4b6a719f668f12fdb4999afaeef62648/tenacity/retry.py#L86
class retry_if_not_exception_type(retry_if_exception):
	"""Retries except an exception has been raised of one or more types."""

	def __init__(self, exception_types=Exception):
		self.exception_types = exception_types
		super(retry_if_not_exception_type, self).__init__(
			lambda e: not isinstance(e, exception_types))


class BadRequest(Exception):
	pass


# ==== GQL : Events ====

CREATE_GQL = gql("""
mutation createEvent($organizerActorId: ID!, $attributedToId: ID, $title: String!, $description: String!, $beginsOn: DateTime!, $endsOn: DateTime, $status: EventStatus, $visibility: EventVisibility, $joinOptions: EventJoinOptions, $draft: Boolean, $tags: [String], $picture: MediaInput, $onlineAddress: String, $phoneAddress: String, $category: EventCategory, $physicalAddress: AddressInput, $options: EventOptionsInput, $contacts: [Contact]) {
  createEvent(organizerActorId: $organizerActorId, attributedToId: $attributedToId, title: $title, description: $description, beginsOn: $beginsOn, endsOn: $endsOn, status: $status, visibility: $visibility, joinOptions: $joinOptions, draft: $draft, tags: $tags, picture: $picture, onlineAddress: $onlineAddress, phoneAddress: $phoneAddress, category: $category, physicalAddress: $physicalAddress, options: $options, contacts: $contacts) {
	id
	uuid
	url
  }
}
""")

UPDATE_GQL = gql("""
mutation updateEvent($id: ID!, $title: String, $description: String, $beginsOn: DateTime, $endsOn: DateTime, $status: EventStatus, $visibility: EventVisibility, $joinOptions: EventJoinOptions, $draft: Boolean, $tags: [String], $onlineAddress: String, $phoneAddress: String, $organizerActorId: ID, $attributedToId: ID, $category: EventCategory, $physicalAddress: AddressInput, $options: EventOptionsInput, $contacts: [Contact]) {
  updateEvent(eventId: $id, title: $title, description: $description, beginsOn: $beginsOn, endsOn: $endsOn, status: $status, visibility: $visibility, joinOptions: $joinOptions, draft: $draft, tags: $tags, onlineAddress: $onlineAddress, phoneAddress: $phoneAddress, organizerActorId: $organizerActorId, attributedToId: $attributedToId, category: $category, physicalAddress: $physicalAddress, options: $options, contacts: $contacts) {
	id
	uuid
  }
}
""")

UPDATE_GQL_ORIG = gql("""
mutation updateEvent($id: ID!, $title: String, $description: String, $beginsOn: DateTime, $endsOn: DateTime, $status: EventStatus, $visibility: EventVisibility, $joinOptions: EventJoinOptions, $draft: Boolean, $tags: [String], $picture: PictureInput, $onlineAddress: String, $phoneAddress: String, $organizerActorId: ID, $attributedToId: ID, $category: String, $physicalAddress: AddressInput, $options: EventOptionsInput, $contacts: [Contact]) {
  updateEvent(eventId: $id, title: $title, description: $description, beginsOn: $beginsOn, endsOn: $endsOn, status: $status, visibility: $visibility, joinOptions: $joinOptions, draft: $draft, tags: $tags, picture: $picture, onlineAddress: $onlineAddress, phoneAddress: $phoneAddress, organizerActorId: $organizerActorId, attributedToId: $attributedToId, category: $category, physicalAddress: $physicalAddress, options: $options, contacts: $contacts) {
	id
	uuid
  }
}
""")


CANCEL_GQL = gql("""
mutation updateEvent($eventId: ID!) {
  updateEvent(eventId: $eventId, status: CANCELLED) {
	id
	uuid
  }
}
""")

CONFIRM_GQL = gql("""
mutation updateEvent($eventId: ID!) {
  updateEvent(eventId: $eventId, status: CONFIRMED) {
	id
	uuid
  }
}
""")


DELETE_GQL = gql("""
mutation DeleteEvent($eventId: ID!) {
  deleteEvent(eventId: $eventId) {
	id
  }
}
""")

# ==== /GQL : Events ====

# ==== GQL : Actors ====

CREATE_USER_GQL = gql("""
mutation createUser($email: String!, $locale: String="fr", $password: String!) {
  createUser(email: $email, locale: $locale, password: $password) {
	id
  }
}""")

CREATE_GROUP_GQL = gql("""
mutation createGroup($name: String, $preferredUsername: String!, $summary: String = "") {
  createGroup(name: $name, preferredUsername: $preferredUsername, summary: $summary) {
	id
  }
}""")

CREATE_PERSON_GQL = gql("""
mutation createPerson($name: String, $preferredUsername: String!, $summary: String = "") {
  createPerson(name: $name, preferredUsername: $preferredUsername, summary: $summary) {
	id   url
  }
}""")

CREATE_MEMBER_GQL = gql("""
mutation inviteMember($groupId: ID!, $targetActorUsername: String!) {
  inviteMember(groupId: $groupId, targetActorUsername: $targetActorUsername) {
	id   role
  }
}""")

UPDATE_MEMBER_GQL = gql("""
mutation updateMemberRole($memberId: ID!, $role:MemberRoleEnum!) {
  updateMember(memberId: $memberId, role: $role) {
	id   role
  }
}""")

# ==== /GQL : Users ====

# ==== GQL : credentials ====

LOGIN_GQL = gql("""
mutation login($email: String!, $password: String!) {
  login(email: $email, password: $password) {
	accessToken   refreshToken
  }
}""")

REFRESH_TOKEN_GQL = gql("""
mutation RefreshToken($rt:String!) {
  refreshToken(refreshToken: $rt) {
	accessToken   refreshToken
  }
}""")

LOGOUT_GQL = gql("""
mutation logout($rt: String!) {
  logout(refreshToken: $rt)
}""")

# ==== /GQL : credentials ====

# ==== GQL : identities - actors - persons and groups ====

PROFILES_GQL = gql("""
query Identities { identities { ...ActorFragment } }
fragment ActorFragment on Actor { id type preferredUsername name url}
""")

GROUPS_GQL = gql("""
query LoggedUserMemberships($membershipName: String, $page: Int, $limit: Int) {
  loggedUser {
	memberships(name: $membershipName, page: $page, limit: $limit) {
	  elements {
		role
		actor { ...ActorFragment }
		parent { ...ActorFragment }
	  }
	}     
  }
}
fragment ActorFragment on Actor {  id type  preferredUsername  name }
""")

EVENTS_LU_GQL = gql("""
query {
  loggedUser {
    id
    actors {
      id
      name
      organizedEvents(limit: 1000) {
        elements {
          id
          title
          description
          beginsOn
          endsOn
          status
          visibility
          joinOptions
          draft
          tags {id slug}
          picture {url}
          onlineAddress
          phoneAddress
          category
          physicalAddress {country}
          options {isOnline}
          contacts {name}
        }
      }
    }
  }
}

""")

# Low level Mobilizon API
class Mobilizon():
	__slots__ = 'client'

	def __init__(self, endpoint, bearer=None):
		self.client = self._build_client(endpoint, bearer)

	# events

	def create_event(self, actor_id, variables):
		variables["organizerActorId"] = actor_id
		return self._publish(CREATE_GQL, variables)

	def update_event(self, actor_id, variables):
		variables["organizerActorId"] = actor_id
		return self._publish(UPDATE_GQL, variables)

	def confirm_event(self, event_id):
		variables = dict()
		variables["eventId"] = event_id
		return self._publish(CONFIRM_GQL, variables)

	def cancel_event(self, event_id):
		variables = dict()
		variables["eventId"] = event_id
		return self._publish(CANCEL_GQL, variables)

	def delete_event(self, actor_id, event_id):
		variables = { "actorId": actor_id,
			"eventId" : event_id }
		return self._publish(DELETE_GQL, variables)

	# actors

	def create_user(self, email, password):
		variables = dict()
		variables["email"] = email
		variables["password"] = password
		return self._publish(CREATE_USER_GQL, variables)

	def create_person(self, name, preferredUsername, summary = ""):
		variables = dict()
		variables["name"] = name
		variables["preferredUsername"] = preferredUsername
		variables["summary"] = summary
		return self._publish(CREATE_PERSON_GQL, variables)['createPerson']

	def create_group(self, name, preferredUsername, summary = ""):
		variables = dict()
		variables["name"] = name
		variables["preferredUsername"] = preferredUsername
		variables["summary"] = summary
		return self._publish(CREATE_GROUP_GQL, variables)['createGroup']

	def create_member(self, group_id, preferredUsername):
		variables = dict()
		variables["groupId"] = group_id
		variables["targetActorUsername"] = preferredUsername
		return self._publish(CREATE_MEMBER_GQL, variables)['inviteMember']

	def update_member(self, memberId, role):
		variables = dict()
		variables["memberId"] = memberId
		variables["role"] = role
		return self._publish(UPDATE_MEMBER_GQL, variables)['updateMember']

	# users / credentials

	def login(self, email, password):
		variables = dict()
		variables["email"] = email
		variables["password"] = password
		data = self._publish(LOGIN_GQL, variables)
		login = data['login']
		return login['accessToken'], login['refreshToken']

	def logout(self, rt):
		variables = dict()
		variables["rt"] = rt
		return self._publish(LOGOUT_GQL, variables)  # void

	def refresh_token(self, refresh_token:str):
		variables = dict()
		variables = { 'rt':refresh_token }
		return self._publish(REFRESH_TOKEN_GQL, variables)

	def user_identities(self):
		variables = dict()
		data = self._publish(PROFILES_GQL, variables)
		profiles = data['identities']
		return profiles

	def user_memberships(self):
		variables = { "limit": 20 }
		data = self._publish(GROUPS_GQL, variables)
		memberships = data['loggedUser']['memberships']['elements']
		return memberships

	# events
	
	def list_events(self, identity):
		variables = { }
		data = self._publish(EVENTS_LU_GQL, variables)
		data = data['loggedUser']['actors']
		for actor in data:
			if int(actor['id']) == identity:
				return actor['organizedEvents']['elements']
		return []


	# interns

	def _build_client(self, endpoint, bearer=None):
		headers = dict()
		if bearer is not None:
			headers['Authorization']='Bearer '+bearer
		transport = RequestsHTTPTransport(
			url=endpoint,
			headers=headers,
			verify=True,
			#retries=3,
		)
		return Client(transport=transport)


	# attempts at 0s, 2s, 4s, 8s
	@retry(reraise=True, retry=retry_if_not_exception_type(BadRequest), stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2))
	def _publish(self, mutation, variables):
		try:
			r = self.client.execute(mutation, variable_values=variables)
		except HTTPError as e:
			if e.response.status_code in [400,404]:
				raise BadRequest(e)
			else:
				raise
		except TransportQueryError as e:
			raise BadRequest(e)
		except:
			raise
		return r


# High-level Mobilizon API
class MobilizonClient():
	def __init__(self, endpoint, bearer=None):
		self.endpoint = endpoint
		self.bearer = bearer
		self.identity = 0
		self.preferred_username = None

	def login(self, email, password, identity=0):
		r = Mobilizon(self.endpoint, self.bearer).login(email, password)
		self.bearer = r[0]
		self.identity = identity
		if not self.identity:
			ids = self.identities()
			self.identity = ids[0]['id']
	
	def identities(self):
		return Mobilizon(self.endpoint, self.bearer).user_identities()

	def memberships(self):
		return Mobilizon(self.endpoint, self.bearer).user_memberships()

	def list_events(self):
		r = Mobilizon(self.endpoint, self.bearer).list_events(self.identity)
		events = []
		for event_dict in r:
			events.append(MobilizonEvent.from_dict(event_dict))
		
		return events

	def create_event(self, title, beginsOn, endsOn=None, description="", actor_id=None, status="CONFIRMED", visibility="PRIVATE", joinOptions=None, draft=False, tags=None, picture=None, onlineAddress=None, phoneAddress=None, category=None, physicalAddress=None, options=None, contacts=None):
		if not actor_id:
			actor_id = self.identity
		if not endsOn:
			endsOn = beginsOn
		variables = {
			"title": title, 
			"description": description,
			"beginsOn": beginsOn.isoformat(),
			"endsOn": endsOn.isoformat(),
			"status": status, # CANCELLED / CONFIRMED / TENTATIVE
			"visibility": visibility, # PRIVATE, PUBLIC, RESTRICTED, UNLISTED
			"joinOptions": joinOptions,
			"draft": draft,
			"tags": tags,
			"picture": picture,
			"onlineAddress": onlineAddress,
			"phoneAddress": phoneAddress,
			"category": category,
			"physicalAddress": physicalAddress,
			"options": options,
			"contacts": contacts
		}
		filtered_variables = {k: v for k, v in variables.items() if v is not None}
		r = Mobilizon(self.endpoint, self.bearer).create_event(actor_id, filtered_variables)
		return r['createEvent']

	def create_event_from_dict(self, event, actor_id=None):
		if not actor_id:
			actor_id = self.identity
		event["beginsOn"] = event["beginsOn"].isoformat()
		event["endsOn"] = event["endsOn"].isoformat()
		
		# TODO: Doesn't work! Don't use picture.
		if event.get("picture"):
			media = { "url": event["picture"] }
			event["picture"] = media
		r = Mobilizon(self.endpoint, self.bearer).create_event(actor_id, event)
		return r['createEvent']

	def delete_event(self, event_id):
		r = Mobilizon(self.endpoint, self.bearer).delete_event(self.identity, event_id)
		return r['deleteEvent']['id']
	
	def update_event(self, event):
		variables = event.get_dict()
		variables["beginsOn"] = variables["beginsOn"].isoformat()
		variables["endsOn"] = variables["endsOn"].isoformat()
		r = Mobilizon(self.endpoint, self.bearer).update_event(self.identity, variables)
		return r['updateEvent']['id']


if __name__ == "__main__":
	import sys
	operation = sys.argv[1]
	email = sys.argv[2]
	password = sys.argv[3]
	endpoint = sys.argv[4]
	identity = int(sys.argv[5])

	client = MobilizonClient(endpoint)
	client.login(email, password, identity)
	identities = client.identities()
	print ('Identities:')
	for id in identities:
		print(' - ', id['id'], id['preferredUsername'])
		if int(id['id']) == client.identity:
			client.preferred_username = id['preferredUsername']
	print('Preferred username:', client.preferred_username)
	print ('Memberships:', client.memberships())
	events = client.list_events()
	print ('Events:')
	for event in events:
		print(' - ', event.id, event.title)
		if operation == 'deleteall':
			print('Deleting:', client.delete_event(event.id))

