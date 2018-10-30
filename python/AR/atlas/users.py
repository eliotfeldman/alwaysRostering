import csv
import json
import logging
from bs4 import BeautifulSoup
import re
from AR.atlas import constants
import asyncio
import pprint

pp = pprint.PrettyPrinter(indent=4)

class Users():
    """
    Handles users operations
    """
    @classmethod
    async def create(cls, session, map_file):
        """
        Creates an object linked to a session
        Need a factory function due to async
        """
        self = cls()
        self.session = session
        self.users = await self.load()
        self.map_file = map_file
        self.id_map = self.load_map()
        return self

    async def parse_page(self, url):
        """
        GETs and parses a users page, returnling a list of user dicts
        """
        users = []

        resp = await self.session.get(url)
        soup = BeautifulSoup(await resp.text(), 'html.parser')
        rows = soup('tr', {'class': 'Teacher'})
        for row in rows[1:]: # Skip the first row
            user = {}
            user['atlas_id'] = re.search('Teacher_row_(.*)', row['id']).group(1)
            td = list(row('td'))
            name = td[0].string.split(', ')
            user['last_name'] = name[0]
            user['first_name'] = name[1]
            emails = list(td[1].stripped_strings)
            user['email'] = emails[0]
            user['attributes'] = []
            for attribute in td[2].stripped_strings:
                user['attributes'].append(attribute)
            user['priveleges'] = []
            for priveleges in td[3].stripped_strings:
                user['priveleges'].append(priveleges)
            users.append(user)
        return users

    def load_map(self):
        """
        Atlas does not have a place to store our IDs, so we have to keep a
        separate map of them. We use a CSV file to make it easy to edit. This
        function loads the CSV
        """
        id_map = []
        with open(self.map_file, newline='') as csvfile:
            reader  = csv.DictReader(csvfile)
            for row in reader:
                id_map.append(row)
        return id_map

    def save_map(self):
        """
        Write the ID map to a CSV file
        """
        with open(self.map_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, ["atlas_id", "genesis_id"])
            writer.writeheader()
            for row in self.id_map:
                writer.writerow(row)
            
    async def load(self):
        """
        Loads / parses the users pages on Atlas to create a users list
        """
        # see how many pages there are
        resp = await self.session.get(constants.BASE_URL +
            'Atlas/Admin/View/Teachers')
        soup = BeautifulSoup(await resp.text(), 'html.parser')
        span = soup.find('span', {'class': 'UIPagingShowing'})
        max_pages = int(re.search('\(Page 1 of (\d+), Records.*',
            span.contents[0]).group(1))

        # Load all the pages asynchronously
        logging.debug("Loading {} pages of users".format(max_pages))
        tasks = []
        for page in range(1, max_pages + 1):
            tasks.append(self.parse_page(constants.BASE_URL + 
                'Atlas/Admin/View/Teachers?Page={}'.format(page)))

        # Gather the results and setup our users list
        users = []
        for chunk in await asyncio.gather(*tasks):
            users += chunk
        return users

    def find_by_email(self, email):
        """
        Case insensitive email search that returns first match
        """
        for user in self.users:
            if user['email'].lower() == email.lower():
                return user
        return None

    def find_by_name(self, first_name, last_name):
        """
        Case insensitive first and last name search that returns first match
        """
        for user in self.users:
            if user['last_name'].lower() == last_name.lower() and user['first_name'].lower() == first_name.lower():
                return user
        return None

    async def save_object(self, atlas_id, first_name, last_name, email, admin):
        """
        Adds a user to Atlas. The POST request is URL encoded JSON
        """
        json_data = {
            "Save": {
                "Object": {
                    "Populate": False,
                    "Type": "Teacher",
                    "ID": atlas_id,
                    "WebPass": "",
                    "HasCustomizedMyAtlas": "",
                    "EmailAlert": "1",
                    "ExemplarTeachNoCourseCertified": "",
                    "ExemplarUnitSubmitted": "",
                    "NumberOfExemplarVisits": "",
                    "PasswordEncrypted": "",
                    "PasswordRequested": "",
                    "LastExemplarVisited": "",
                    "HarvestEmailSent": "",
                    "LastSiteNoticeID": "",
                    "AcceptedExemplarAgreement": "",
                    "PropertiesXML": "",
                    "ReceivedAtlasUpdate": "",
                    "TeacherLast": last_name,
                    "TeacherFirst": first_name,
                    "Email": email,
                    "TeacherIsCoreTeam": "",
                    "TeacherWidgetConfigurationGroupID": "",
                    "TeacherIsAdmin": admin if admin else "",
                    "WillSendWelcomeEmail": "",
                    "SchoolMessaging": "",
                    "SendInvitationEmail": ""
                },
                "Method": "AsyncSave",
                "Parameters":{}
            }
        }
        form_data = {'Actions': json.dumps(json_data)}
        resp = await self.session.post(constants.BASE_URL +
            'Atlas/Controller', data=form_data)
        response_json = await resp.json(content_type=None)
        message = response_json['Save']
        if 'ID' not in message:
            logging.error("Unable to save_object {} {} {} {}: {}".format(first_name,
                last_name, email, genesis_id, message))
            return None
        return message['ID']

    def atlas_to_genesis(self, atlas_id):
        """
        Converts an Atlas ID to a Genesis ID using the id_map
        """
        for pair in self.id_map:
            if pair['atlas_id'] == atlas_id:
                return pair['genesis_id']
        return None

    def genesis_to_atlas(self, genesis_id):
        """
        Converts a Genesis ID to an Atlas ID using the id_map
        """
        for pair in self.id_map:
            if pair['genesis_id'] == genesis_id:
                return pair['atlas_id']
        return None

    async def add_update(self, genesis_id, first_name, last_name, email,
        admin=False):
        """
        Adds or updates a user handling the id_map. If the genesis id is in the
        id_map it is considered an update, otherwise it is an add
        """
        atlas_id = self.genesis_to_atlas(genesis_id)
        if atlas_id == None:
            atlas_id = await self.save_object("", first_name, last_name, email, admin)
            id_map.append({'atlas_id': atlas_id, 'genesis_id': genesis_id})
        else:
            await self.save_object(atlas_id, first_name, last_name, email, admin)

    async def delete_object(self, atlas_id):
        """
        Deletes a user from Atlas. The POST request is URL encoded JSON
        """
        json_data = {
            "Delete": {
                "Object": {
                    "Populate": False,
                    "Type": "Teacher",
                    "TeacherID": atlas_id,
                },
                "Method": "AsyncDelete",
                "Parameters":{},
            }
        }
        form_data = {'Actions': json.dumps(json_data)}
        resp = await self.session.post(constants.BASE_URL +
            'Atlas/Controller', data=form_data)
        response_json = await resp.json(content_type=None)
        message = response_json['Delete']
        if message['Result'] != 'OK':
            logging.error("Unable to delete_object {}: {}".format(atlas_id, message))
