import asyncio
import logging
import sys
import datetime

import AR.AR as AR
from AR.tables import Student as GenesisStudent
import AR.credentials as credentials
import AR.education_city as edcity
import AR.education_city.constants as ec_constants

async def sync(loop):
    school_code = 'MLS'
    async with edcity.Session(school_code, loop) as EducationCity:

        # Start downloading the current Education City user database
        print("Downloading users in background...")
        download_task = loop.create_task(EducationCity.download())
        await asyncio.sleep(0.25) # give the requests a chance to fire

        # Build new lists of what the users should be
        print("Building user lists...")
        students = {} 
        for genesis_student in (AR.students()
            .filter(GenesisStudent.current_school==school_code)
            .filter(GenesisStudent.grade_level.in_(['KH', 'KF', '01', '02', '03']))):
            # NOTE: There are differences between attribute names used in
            # bulk_user_management and those returned by the user API
            ec_student = {
                'user_defined_id': genesis_student.student_id,
                'first_name': genesis_student.first_name, 
                'last_name': genesis_student.last_name,
                'class_name': genesis_student.homeroom_name,
                'username': genesis_student.simple_username,
                'password': genesis_student.simple_password,
                'gender': genesis_student.gender.lower(),
                'date_of_birth': genesis_student.date_of_birth.strftime('%m/%d/%Y'),
                'academic_year': genesis_student.academic_level,
            }
            students[genesis_student.student_id] = ec_student

        await download_task

        print("Saving previous users...")
        await EducationCity.save(f'{school_code}.json')

        ec_students = EducationCity.users[ec_constants.USERTYPE_STUDENT]
        ec_genesis_ids = set(EducationCity.users[ec_constants.USERTYPE_STUDENT].keys())
        new_genesis_ids = set(students.keys())

        # Delete students in Education City but not in our newly created list
        deletes = ec_genesis_ids - new_genesis_ids
        print(f"Deleting {len(deletes)} students...")
        for genesis_id in deletes:
            name = ec_students[genesis_id]['fullname']
            print(f"[DEL] {genesis_id} {name}")

        # Add students in our new list but NOT in Education City
        adds = new_genesis_ids - ec_genesis_ids
        student_adds = []
        print(f"Adding {len(adds)} students...")
        for genesis_id in adds:
            student = students[genesis_id]
            name = student['first_name'] + " " + student['last_name']
            print(f"[ADD] {genesis_id} {name}")
            student_adds.append(student)
        #await EducationCity.addmod_students(student_adds)

        # Check the overlap to see if any students need to be updated
        student_mods = []
        print("Checking if students to be modified...")
        for genesis_id in ec_genesis_ids.intersection(new_genesis_ids):
            student_old = ec_students[genesis_id]
            student_new = students[genesis_id]
            student_new['id'] = student_old['id'] # Education City IDs don't change
            name = student_new['first_name'] + " " + student_new['last_name']
            # Compare all the attributes we care about
            modify = False;
            for pair in [('first_name', 'firstname'),
                ('last_name', 'lastname'), ('class_name', 'className'),
                ('username', 'username'), ('gender', 'gender'),
                ('academic_year', 'yearString'), ('date_of_birth', 'dob')]:
                if pair[0] == 'date_of_birth': # Date format is different
                    attribute1 = (datetime.datetime
                        .strptime(student_new['date_of_birth'], '%m/%d/%Y')
                        .strftime('%d/%m/%Y'))
                else:
                    attribute1 = student_new[pair[0]]
                attribute2 = student_old[pair[1]]
                if attribute1 != attribute2:
                    print(f"[MOD] {genesis_id} {name}: '{attribute2}'->'{attribute1}'")
                    modify = True;
            if modify:
                student_mods.append(student_new)
                
logging.basicConfig(level=logging.DEBUG)
AR.init('/home/ryan/alwaysRostering/python/databases/2019-01-29-genesis.db')
loop = asyncio.get_event_loop()
loop.run_until_complete(sync(loop))
