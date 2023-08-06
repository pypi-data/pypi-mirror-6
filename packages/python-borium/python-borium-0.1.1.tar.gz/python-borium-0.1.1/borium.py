"""Simple Get/Put API for the Borium Queue.

Usage:

import borium

borium.get(job_type)
borium.put(job_type, config)

In both instances, job_type is a string that specifies the job that is to be
enqueued. The config, though usually dependent on the job itself, is usually
a JSON object containing the configuration as required per job.
"""

import sys
import json
import socket
import time

__config = None
__config_path = '/etc/borium/configuration.json'

def __configure():
    """Reads and parses the configuration JSON file"""
    global __config, __config_path
    __config =  json.load(open(__config_path))

def get(job_type):
    """Creates and requests a get query for the specified job type"""
    return __request('get:' + job_type + ':')

def put(job_type, config):
    """Creates and requests a put query for the specified job type and config."""
    return __request('put:' + job_type + ':' + config)

def __request(query):
    """Sends the query to the borium queue through a TCP socket"""
    global __config

    for i in range(10):
        try:
            borium_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            host = __config.get('host', 'localhost')

            borium_socket.connect((host, __config['port']))
            borium_socket.send(query+"\n")
            borium_socket.send("\n")

            data = ''
            while 1:
                line = borium_socket.recv(1024)
                if not line: break
                data += line
            print(data)

            borium_socket.close()

            return json.loads(data)

        except Exception as e:
            print >> sys.stderr, e
            time.sleep(1)
            continue

__configure()
