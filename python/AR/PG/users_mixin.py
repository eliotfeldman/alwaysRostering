from bs4 import BeautifulSoup
from AR.PG.user import User
import asyncio
import logging
import sys

class UsersMixin():
    """
    This mixin provides routines for dealing with PG users
    """
    async def parse_user_profile(self, url):
        """
        Loads a user profile page, parses it and returns a user object
        """
        resp = await self.get(url)
        html = await resp.text()
        user = User(html=html)
        return user
        
    async def load_users(self):
        """
        Gets a list of all users on PG and returns it
        """
        resp = await self.get('https://www.mylearningplan.com/DistrictAdmin/UserList.asp?V=ALL')
        soup = BeautifulSoup(await resp.text(), 'html.parser')
        tasks = []
        for link in soup('a'):
            href = link.get('href')
            if href.startswith('/Forms.asp?F=INT_USERID&M=E&I='):
                tasks.append(self.parse_user_profile('https://www.mylearningplan.com' + href))
        users = []
        for user in await asyncio.gather(*tasks):
            users.append(user)
        return users

    def user_by_name(self, first, last):
        """
        Performs a CASE INSENSITIVE search for a user based on first and last name
        """
        for user in self.users:
            if first.upper() == user.first_name.upper() and last.upper() == user.last_name.upper():
                return user
        return None

    def user_by_payroll(self, payroll_id):
        """
        Performs search for a user based on their payroll ID
        """
        for user in self.users:
            if user.payroll_id ==  payroll_id:
                return user
        return None

    def user_by_id(self, pg_id):
        """
        Performs search for a user based on their PG id
        """
        for user in self.users:
            if user.pg_id ==  pg_id:
                return user
        return None

    async def save_user(self, user):
        """
        Saves a user object on PG
        """
        resp = await self.post('https://www.mylearningplan.com/Forms.asp',
            data=user.data())
        soup = BeautifulSoup(await resp.text(), 'html.parser')
        if list(soup.find('h1').strings)[0] != 'Confirmation':
            logging.error("Error while saving user {}")
            sys.exit(1)
