"""
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
import requests

# TODO: MUST SANITIZE THIS FILE BEFORE PUBLISHING!!!!!!
# WebEx API Bot Setup
BASE_URL = 'https://webexapis.com/v1'
BOT_NAME = ''
BOT_USERNAME = '@webex.bot'
BOT_ID = ''
BOT_ACCESS_TOKEN = ''

# Webex Person ID used for Direct reporting
PERSON_ID = ''


def post_Webex_Message(message):
	"""
	Cisco Webex API call to have the defined Bot POST a Message
	:param message:
	:return:
	"""
	url = '{}/messages'.format(BASE_URL)
	hdr = {
		'Authorization': 'Bearer {}'.format(BOT_ACCESS_TOKEN),
		'Content-Type': 'application/json'
	}
	# Defining Message characteristics
	payload = {
		'markdown': message,
		'toPersonId': PERSON_ID
	}

	response = requests.request('POST', url, headers=hdr, json=payload)
	return response.json()
