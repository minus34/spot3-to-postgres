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
import psycopg2  # need to install psycopg2-binary package
import psycopg2.extras
import ssl
import urllib.request

from psycopg2.extensions import AsIs

settings = dict()

# postgres settings
settings["pg_schema"] = "public"
settings["pg_points_table"] = "spot3_points"
settings["pg_lines_table"] = "spot3_lines"
settings["pg_connect_string"] = "dbname=geo host=localhost port=5432 user=postgres password=password"

# SPOT3 API
settings["api_url"] = "https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/16eXyDLztlnvBYOYclTKcyfLas4rM2pvI/message?start=50&limit=500&license=null&expiryDate=null&feedPassword=password"
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
    if message_list is not None:
        # insert new records into postgres table
        insert_new_records(pg_cur, message_list)
    else:
        logger.fatal("Couldn't download SPOT3 JSON feed")


# download and parse JSON
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


# insert messages, one at a time
def insert_new_records(pg_cur, message_list):

    rows_inserted = 0

    # for each message - only insert if new
    for message_dict in message_list:
        if message_dict["unixTime"] > 1564616366:
            # remove unwanted value
            message_dict.pop("@clientUnixTime", None)

            # get column names and values for inserting
            columns = message_dict.keys()
            values = [message_dict[column] for column in columns]

            # use "UPSERT" to insert new data only
            insert_statement = "INSERT INTO {}.{} (%s) VALUES %s ON CONFLICT (messengerId, unixTime) DO NOTHING" \
                .format(settings["pg_schema"], settings["pg_points_table"])
            pg_cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))

            rows_inserted += pg_cur.rowcount

    logger.info("{} new records inserted".format(rows_inserted))

    # add point geometries to table
    sql = """UPDATE {}.{}
               SET geom = ST_SetSRID(ST_MakepointM(longitude, latitude, unixTime), 4283)
               WHERE geom is null""".format(settings["pg_schema"], settings["pg_points_table"])
    pg_cur.execute(sql)

    # update table stats
    pg_cur.execute("ANALYSE {}.{}".format(settings["pg_schema"], settings["pg_points_table"]))

    # refresh lines view
    pg_cur.execute("refresh materialized view {}.{}".format(settings["pg_schema"], settings["pg_lines_table"]))


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

    task_name = "Import SPOT3 data"

    logger.info("{} started".format(task_name))

    main()

    time_taken = datetime.datetime.now() - full_start_time
    logger.info("{0} finished : {1}".format(task_name, time_taken))

