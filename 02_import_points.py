"""
-----------------------------------------------------------------------------------------------------------------------
Purpose:     Imports GPS points from the SPOT3 API into Postgres/PostGIS

Author:      Hugh Saalmans

Created:     01/08/2019

License:     Apache 2.0
-----------------------------------------------------------------------------------------------------------------------
"""

import datetime
import json
import os
import psycopg2  # @2 - need to install psycopg2-binary package
import psycopg2.extras
import ssl
import urllib.request

from psycopg2.extensions import AsIs

settings = dict()

# where to save the current S3 file for debugging (if something goes pear shaped on import to postgres)
settings["debug_file_path"] = '/Users/s57405/tmp/'

# the path to this script - DO NOT EDIT
settings["script_dir"] = os.path.dirname(os.path.realpath(__file__))

# set postgres script director
settings["sql_dir"] = os.path.join(settings["script_dir"], "postgres-scripts")

# postgres settings
settings["pg_schema"] = "public"
settings["pg_points_table"] = "tag_reports"
settings["pg_connect_string"] = "dbname=geo host=localhost port=5432 user=postgres password=password"

# SPOT3 API
settings["api_url"] = "https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/16eXyDLztlnvBYOYclTKcyfLas4rM2pvI/message?license=null&expiryDate=null&feedPassword=password"
settings["encoding"] = "utf-8"

def main():
    # connect to Postgres
    try:
        pg_conn = psycopg2.connect(settings["pg_connect_string"])
        pg_conn.autocommit = True
        pg_cur = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        logger.debug("Connected to Postgres")
    except Exception as e:
        message = "Unable to connect to database : {}".format(e)
        logger.error(message)
        return False

    # download latest JSON
    message_list = get_json(settings["api_url"], settings["encoding"])
    if message_list is None:
        logger.fatal("Couldn't download SPOT3 JSON feed")

    # insert new records into postgres table


# insert messages, one at a time
def parse_and_insert_new_records(pg_cur, root_elem):

    # Step through XML and extract each message's data, then insert it into the database
    try:
        for i in root_elem.iter('messages'):
            guid = get_xml_string(i, 'guid')
            guid = guid.split("/")[-1]  # Take the id number out of the full guid to remove the unwanted URL
            title = get_xml_string(i, 'title')
            category = get_xml_string(i, 'category').upper()
            link = get_xml_string(i, 'link')
            description = get_xml_string(i, 'description')

            # add points to temp table
            for pnt in i.iter('{http://www.georss.org/georss}point'):
                xy_array = pnt.text.split()
                x = xy_array[1]
                y = xy_array[0]
                wkt_point = ''.join(["ST_SetSRID(ST_MakePoint(", x, ",", y, "),4283)"])


            # # for output_event in output_event_list:
            # columns = event.keys()
            # values = [event[column] for column in columns]
            #
            # insert_statement = "INSERT INTO {}.{} (%s) VALUES %s" \
            #     .format(settings["pg_schema"], settings["pg_points_table"])
            #
            # pg_cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
            # # print(pg_cur.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))

    except:
        logger.exception("Couldn't process XML data")
        return False


# download XML file and parse it into XML ElementTree
def get_json(url, encoding):

    try:
        ssl_context = ssl.SSLContext()
        response = urllib.request.urlopen(url, context=ssl_context)
        response_string = response.read()
        json_string = response_string.decode(encoding)
    except Exception as e:
        json_string = None
        logger.fatal("Couldn't download and decode file : {}".format(e))

    # parse json string and return list of messages
    if json_string is not None:
        try:
            return json.loads(json_string)["response"]["feedMessageResponse"]["messages"]["message"]
        except Exception as e:
            logger.fatal("Failed to parse JSON : {}".format(e))
            return None


def get_xml_string(element, name, show_error=True):
    try:
        return element.find(name).text.strip()
    except AttributeError:
        if show_error:
            logger.warning("XML missing element '{}'".format(name,))
        return ""


def check_if_new_record(pg_cur, messenger_id, unix_time):
    # check if data already in postgres
    sql = "SELECT EXISTS (SELECT 1 FROM {}.{} WHERE messengerId = '{}' AND unixTime = {} LIMIT 1)" \
        .format(settings["pg_schema"], settings["pg_points_table"], messenger_id, unix_time)
    pg_cur.execute(sql)

    if pg_cur.fetchone()[0]:
        return False
    else:
        return True


if __name__ == '__main__':
    full_start_time = datetime.datetime.now()

    import logging
    logger = logging.getLogger()

    # set logger
    log_file = os.path.abspath(__file__).replace(".py", ".log")
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format="%(asctime)s %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S %p")

    # setup logger to write to screen as well as writing to log file
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    task_name = "import SPOT3 data"

    logger.info("{} started".format(task_name))

    main()

    time_taken = datetime.datetime.now() - full_start_time
    logger.info("{0} finished : {1}".format(task_name, time_taken))
    logger.info("")