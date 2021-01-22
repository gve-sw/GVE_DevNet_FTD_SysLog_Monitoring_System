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
import json
from werkzeug.security import check_password_hash, generate_password_hash


class FMC (object):
	"""
	Class to define the FMC Connection Object used.
	NOTE: For verbose testing output, feel free to uncomment print statements from fuctions!
	"""

	def __init__(self, host, username, password):
		"""
		Initialize the FMC Connection object
		:param: Host - FMC hostname (FQDN OR IP)
		:param: Username - FMC Username for API user
		:param: Password - FMC Password for API user
		"""
		self.host = host
		self.username = username
		self.password = password
		self.baseUrl = "https://{}".format(host)
		self.domainUUID = ""
		self.authToken = ""
		self.refreshToken = ""

	def generate_Token(self):
		"""
		Generate an FMC authentication token.
		"""
		path = "/api/fmc_platform/v1/auth/generatetoken"
		url = "{}{}".format(self.baseUrl, path)

		authentication = requests.auth.HTTPBasicAuth(self.username, self.password)
		headers = {'Content-Type': 'application/json'}

		try:
			response = requests.post(url=url, headers=headers, auth=authentication, verify=False)
			response.raise_for_status()
		except requests.exceptions.HTTPError as err:
			raise SystemExit(err)

		self.password = generate_password_hash(self.password)
		self.authToken = response.headers['X-auth-access-token']
		self.refreshToken = response.headers['X-auth-refresh-token']
		self.domainUUID = response.headers['DOMAIN_UUID']

	def get_Devices(self):
		"""
		Retrieve the known Device records within the FMC's Domain
		:return: FMC REST API response object
		"""
		path = "/api/fmc_config/v1/domain/{}/devices/devicerecords".format(self.domainUUID)
		url = "{}{}".format(self.baseUrl, path)

		headers = {
			'Content-Type': 'application/json',
			'X-auth-access-token': self.authToken
		}

		try:
			response = requests.get(url=url, headers=headers, verify=False)
			response.raise_for_status()
		except requests.exceptions.HTTPError as err:
			raise SystemExit(err)

		jsonResponse = json.loads(response.text)
		return jsonResponse['items']

	def get_HA_Pairs(self):
		"""

		:return:
		"""
		path = "/api/fmc_config/v1/domain/{}/devicehapairs/ftddevicehapairs".format(self.domainUUID)
		url = "{}{}".format(self.baseUrl, path)

		headers = {
			'Content-Type': 'application/json',
			'X-auth-access-token': self.authToken
		}

		try:
			response = requests.get(url=url, headers=headers, verify=False)
			response.raise_for_status()
		except requests.exceptions.HTTPError as err:
			raise SystemExit(err)

		jsonResponse = json.loads(response.content)
		return jsonResponse['items']

	def get_Failover_Mac_Config(self, haPairId):
		"""

		:param haPairId:
		:return:
		"""
		path = "/api/fmc_config/v1/domain/{}/devicehapairs/ftddevicehapairs/{}".format(
			self.domainUUID, haPairId)
		url = "{}{}".format(self.baseUrl, path)

		headers = {
			'Content-Type': 'application/json',
			'X-auth-access-token': self.authToken
		}

		try:
			response = requests.get(url=url, headers=headers, verify=False)
			response.raise_for_status()
		except requests.exceptions.HTTPError as err:
			raise SystemExit(err)

		jsonResponse = json.loads(response.content)
		return jsonResponse
