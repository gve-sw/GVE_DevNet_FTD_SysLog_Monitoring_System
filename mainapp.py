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

"""
Sub-Zero DevNet Prototype
Workflow:
    Start script -> python(3) mainapp.py
    1)The Script will print a brief validation that the backend setup was successful (optional - For testing)
    2)The Script will sit as a background process until the defined Trigger is met.
    3)Once triggered, the Script will notify the System Administrator
    4)Finally, the Script will automate the Failover between the HA pair.
"""

# IMPORT MODULES
import fmc
import bot
import urllib3
import schedule
import time
from paramiko import SSHClient

urllib3.disable_warnings()

# TODO: MODIFY RSYSLOG CONNECTION INFORMATION
SYSLOG_HOSTNAME = ''
SYSLOG_USERNAME = ''
SYSLOG_PASSWORD = ''


def monitoringTask(activeIP):
	"""
	The task performed on the scheduled interval.
	Task:
		1) Establish SSH connection to RSyslog server
		2) Poll logs
		3) Determine if Trigger Criteria is hit
		4) Take the appropriate action
	:return:
	"""
	# Establish connection to RSYSLOG
	print('Connecting to Rsyslog...')
	client = SSHClient()
	client.load_system_host_keys()
	client.connect(SYSLOG_HOSTNAME, username=SYSLOG_USERNAME, password=SYSLOG_PASSWORD)
	print('Connection to Rsyslog Established!')
	print("----------------------------------")

	# Search RSYSLOG for Specified Syslog message
	stdin, stdout, stderr = client.exec_command('echo {} | sudo -S cat /var/log/{}/%FTD-1-104002.log'.format(
		SYSLOG_PASSWORD, activeIP))

	log_Output = stdout.read().decode().strip()
	log_Error = stdout.channel.recv_exit_status()

	# HIT! Trigger Notification (Return code 0)
	if log_Error == 0:
		print("Trigger Found!")
		# Clear Trigger from Syslog
		client.exec_command('echo {} | sudo -S rm /var/log/{}/%FTD-1-104002.log'.format(
			SYSLOG_PASSWORD, activeIP))

		print("Alerting System Admin...")
		print("------------------------")

		# Set Notification Here
		notification_String = "WARNING: Failover Trigger Criteria Hit! Failover Action should be performed."
		bot.post_Webex_Message(notification_String)

	# Trigger Criteria not met
	else:
		print("Syslog Trigger Not Logged Yet...")
		print("----------------------------")


def scheduleTask(activeIP):
	"""
	The function used to schedule the Monitoring Task in a timely manner
	:return:
	"""
	# TODO: Set/Modify frequency of the scheduled the task
	schedule.every(1).minute.do(monitoringTask, activeIP=activeIP)
	print('Monitoring Job Scheduled...')
	print("---------------------------")

	while True:
		schedule.run_pending()
		time.sleep(10)


def endTask():
	"""
	Helper function to clear any scheduled tasks
	:return:
	"""
	schedule.clear()
	print('Job Ended...')


# MAIN SCRIPT
if __name__ == "__main__":
	print('Starting Script...\n')
	# Step 1) Receive and process Arguments
	host = input('Input FMC hostname (FQDN OR IP) []: ')
	username = input('Input FMC Username []: ')
	password = input('Input FMC Password []: ')

	firepower = fmc.FMC(host, username, password)
	firepower.generate_Token()

	# Verbose Output
	print('Established FMC Connection!')
	print("---------------------------")

	# Prompt to select HA pair to manage
	print('\nFound HA Pairs:')
	print("-----------------")
	current_Fmc_HA_Pairs = firepower.get_HA_Pairs()
	for ha_Pair in current_Fmc_HA_Pairs:
		print('Name: {} --> ID = {}'.format(ha_Pair['name'], ha_Pair['id']))
	print()
	ha_Pair_Id = input('Enter the ID of the HA Pair to manage []:')

	# Collect HA Pair Information
	selected_HA_Pair = firepower.get_Failover_Mac_Config(ha_Pair_Id)
	ha_Pair_Failover = selected_HA_Pair['ftdHABootstrap']
	ha_Pair_Active = ha_Pair_Failover['lanFailover']['activeIP']
	ha_Pair_Standby = ha_Pair_Failover['lanFailover']['standbyIP']

	# Verbose Output
	print()
	print('Starting management of the following HA Pair...')
	print('HA Pair: {}'.format(selected_HA_Pair['name']))
	print('Active FTD: {}'.format(ha_Pair_Active))
	print('Standby FTD: {}'.format(ha_Pair_Standby))
	print("---------------------------------------")

	# Step 2) Run Scheduled task
	scheduleTask(ha_Pair_Active)
