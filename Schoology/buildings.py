# System imports
import logging
import asyncio
import click
import sys

# alwaysRostering imports
import AR.AR as AR
import AR.schoology as schoology

# Schoology script imports
import utils

@click.command()
@click.argument('db_file', type=click.Path(exists=True), metavar='DB_FILE')
@click.option('-e', '--environment', default='testing', show_default=True)
@click.option('-d', '--debug', is_flag=True, help="Print debugging statements")
def main(db_file, environment, debug):
    """
    Syncs up Schoology buildings with a Genesis Database

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
    Performs all steps to sync Schoology buildings

    NOTE: Genesis uses the term 'schools' to refer to the individual
    buildings, Schoology uses buildings. In Schoology there is one school,
    'Monroe Township Schools' and currently 8 buildings (AES, BBS, BES, etc.)
    """
    print(f"Loading {db_file}...")
    AR.init(db_file)
    async with schoology.Session(environment) as Schoology:
        print("Syncing buildings with Schoology...")
        async with Schoology.Buildings as Buildings:
            tasks=[]
            for building in AR.schools():
                tasks.append(
                    Buildings.add_update(
                        title=building.school_name,
                        building_code=building.building_code,
                        address1=building.school_address1,
                        address2=building.school_address2,
                        phone=building.school_office_phone,
                        website=building.school_url
                    )
                )
            await utils.task_monitor(tasks, 30)

if __name__ == '__main__':
    main()
