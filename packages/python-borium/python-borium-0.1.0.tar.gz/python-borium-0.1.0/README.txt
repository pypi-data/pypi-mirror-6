=============
python-borium
=============

Borium provides an API for the borium queue. It exposes simple get/set
methods to grab and push jobs.

Borium is a simple queue system written by Kazuyoshi Tlacaelel. To
learn more, visit `the project repository <https://github.com/freshout-dev/borium>`_.

Usage
=====
::

    import borium

    response = borium.put(job_type, config)  # sends the job to the queue
    job = borium.get(job_type)               # fetches a job

In both examples, job_type is a string that specifies the job that is to
be enqueued. The config, though dependent on the job itself, is usually
a JSON object containing the configuration needed.

All requests to the queue will return an object containing a key called
status. In the case of get this can be: nothing, unparseable, error or
found. In the case of put this can be: error or stored.

If the job was found, the object will also include the key "job" which
includes the config string passed.