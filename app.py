# -*- coding: utf-8 -*-
# pylint: disable=locally-disabled, multiple-statements
# pylint: disable=fixme, line-too-long, invalid-name
# pylint: disable=W0703

""" Meetup RSVP stream listener """

import http.client
import json
import sys
from datetime import datetime
from pymysql import cursors, connect, err


# load configuration settings
with open("settings.json") as settings:
    cfg = json.load(settings)

# setup HTTP connection
try:
    http_conn = http.client.HTTPConnection(cfg['http_host'])
    http_conn.request('GET', cfg['stream'])
    http_resp = http_conn.getresponse()
    http_resp.chunked = False
except Exception as e:
    print("ERR: CONNECTION ERROR {}".format(e))
    sys.exit(1)

# setup database connection
try:
    db_conn = connect(host=cfg['db_host'],
                      user=cfg['db_user'],
                      password=cfg['db_password'],
                      db=cfg['db_name'],
                      charset='utf8mb4',
                      cursorclass=cursors.DictCursor)
except err.OperationalError:
    print("ERR: DB CONNECTION ERROR")
    sys.exit(1)


def get_chunk_size():
    """ Get the size in bytes of a complete event from the stream
    :param: none
    :return: int, length of a complete event, in bytes
    """
    size_str = http_resp.read(2)
    while size_str[-2:] != b"\r\n":
        size_str += http_resp.read(1)
    return int(size_str[:-2], 16)


def get_chunk_data(chunk_size):
    """ Get a chunk from the stream of `chunk_size` bytes
    :param: chunk_size: http stream data
    :return: str: chunk from the stream of `chunk_size` bytes
    """
    stream_chunk = http_resp.read(chunk_size)
    http_resp.read(2)
    return stream_chunk


def iter_listen():
    """ stream generator function, yields rsvp events from the stream, as formatted **JSON** strings.
    :param: none.
    :return: json string
    """
    while True:
        chunk_size = get_chunk_size()
        if chunk_size == 0:
            break
        else:
            try:
                yield json.loads(get_chunk_data(chunk_size).decode(errors='ignore'))
            except Exception as e:
                print("ERR1: {}".format(e))


def listen():
    """ activate listener - the agent will read the RSVP stream, and update the database.
    :param: none
    """
    print("INFO: LISTENER IS RUNNING")
    try:
        for i in iter_listen():
            print(i)
            data = json.loads(filter_data(i))
            with db_conn.cursor() as cur:
                cur.execute("INSERT INTO cities (CITY, LAT, LON, DATE, EID, GID, MID) \
                    VALUES(%s,%s,%s,%s,%s,%s,%s)", (data['CITY'], data['LAT'], data['LON'], data['DATE'],
                                                    data['EID'], data['GID'], data['MID'],))
                db_conn.commit()
    except KeyError:
        print("ERR: MISSING KEY")
    except KeyboardInterrupt:
        print("INFO: USER STOPPED PROGRAM")
    except TypeError:
        print("ERR: TYPE ERROR")
    except Exception as e:
        print("ERR: {}".format(e))
    finally:
        db_conn.close()
        print("INFO: DB CONNECTION CLOSED")
        http_conn.close()
        print("INFO: HTTP CONNECTION CLOSED")


def create_table():
    """ initialize the cities table - any content will be deleted"""
    with db_conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS cities;")
        cur.execute("""CREATE TABLE cities (
                    `idx` int(11) NOT NULL AUTO_INCREMENT,
                    `city` VARCHAR(255),
                    `lat` FLOAT(5,2),
                    `lon` FLOAT(5,2),
                    `date` VARCHAR(255),                        
                    `eid` VARCHAR(255),
                    `gid` VARCHAR(255),
                    `mid` VARCHAR(255),
                    PRIMARY KEY (`idx`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;
                   """)
        db_conn.commit()


def filter_data(data):
    """ Setup the filter in use by the listen() function. It will take the rsvp event JSON string,
    and return a JSON string subset of that data.
    :param: json string
    :return: json string
    """
    try:
        result = json.dumps({
            'CITY': data['group']['group_city'],
            'LAT' : data['group']['group_lat'],
            'LON' : data['group']['group_lon'],
            'DATE': datetime.fromtimestamp(int(str(data['event']['time'])[:-3])).strftime('%Y%m%d'),
            'EID' : data['event']['event_id'],
            'GID' : data['group']['group_id'],
            'MID' : data['member']['member_id']})
        print(result)
        return result
    except KeyError as e:
        print("ERR: {}".format(e))
    except Exception as e:
        print("ERR: {}".format(e))


if __name__ == '__main__':
    listen()
