import logging
import asyncio
import AR.AR as AR
import AR.schoology as schoology
import click
import pprint
import sys
import csv
from AR.tables import DistrictTeacher, Student

pp=pprint.PrettyPrinter()

@click.command()
@click.argument('db_file', type=click.Path(exists=True), metavar='DB_FILE')
@click.option('-e', '--environment', default='testing', show_default=True)
@click.option('-d', '--debug', is_flag=True, help="Print debugging statements")
def main(db_file, environment, debug):
    """
    Syncs up Schoology courses with a Genesis Database

    DB_FILE - A sqlite3 file of the Genesis database
    """
    loop = asyncio.get_event_loop()

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    loop.run_until_complete(sync(loop, db_file, environment))
    loop.close()

async def sync(loop, db_file, environment):
    """
    Performs all steps to sync Schoology courses
    """
    print(f"Loading {db_file}...")
    AR.init(db_file)
    total_courses = AR.courses().count()
    print(f"Updating / Adding {total_courses} courses...")
    async with schoology.Session(environment) as Schoology:
        async with Schoology.Courses as Courses:
            tasks = []
            for course in AR.courses():
                building_code = course.school_code
                title = course.course_description
                course_code = course.school_code + ' ' + course.course_code
                sections = []
                for section in course.active_sections:
                    semester = section.semester
                    if semester == 'FY': # There is only ONE full year
                        grading_period = (f"{section.school_year} "
                                          f"{section.semester}")
                    else: # Others are per building
                        grading_period = (f"{section.school_year} "
                                          f"{section.school_code} "
                                          f"{section.semester}")
                    grading_period_id = Schoology.GradingPeriods.lookup_id(grading_period)
                    if grading_period_id == None:
                        logging.warning("Unable to lookup grading period id for "
                                        f"{section.section_school_code} (Are "
                                        "the grading periods synced with "
                                        "Schoology?)")
                    else:
                        sections.append({
                            'title': section.name,
                            'section_school_code': section.section_school_code,
                            'grading_periods': grading_period_id,
                        })
                tasks.append(
                    loop.create_task(
                        Courses.add_update(building_code, title, course_code, sections)
                    )
                )
                await asyncio.sleep(0) # give the task a chance to start
            await asyncio.gather(*tasks)

if __name__ == '__main__':
    main()