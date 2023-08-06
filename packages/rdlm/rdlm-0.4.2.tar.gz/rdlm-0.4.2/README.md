# restful-distributed-lock-manager

## Status (master branch)

[![Build Status](https://travis-ci.org/thefab/restful-distributed-lock-manager.png)](https://travis-ci.org/thefab/restful-distributed-lock-manager)

## What is it ?

`RDLM` (Restful Distributed Lock Manager) is a lock manager over HTTP built on [Tornado][TORNADO].

## Special features

- RESTful interface
- Timeout automatic management (to avoid stale locks)
- Blocking wait for acquiring a lock (with customatizable timeout)
- Very fast (in memory)
- One unique single threaded process
- Can deal with thousands of locks and simultaneous connections
- Administrative password protected requests

## Quickstart

### Installation

    pip install rdlm

    Requirements: 
    - Python 2.6, 2.7, 3.2 or 3.3
    - Tornado >= 2.3
                  
### Starting the daemon

    rdlm-daemon.py --port=8888 --logging=debug

    (rdlm-daemon.py --help for the full list of options)

## Concepts

In `RDLM`, there are only three (easy) concepts :

- the **resource**, which is designed as a simple string (`[a-zA-Z0-9]+` regexp)
- the **lock**, which is always **exclusive** in this version of `RDLM`
- the client, which can acquire or release some locks on resources

For a given resource, at a given time, there is only a maximum of **ONE** exclusive lock acquired.

Of course, clients can be distributed on different machines / networks... without any change on the rule of the exclusive lock.

The lock is defined by 3 incoming parameters :

- the "title" param, which is a simple indicative string about the client requesting the lock (so a kind of "user agent")
- the "lifetime" param (in seconds), which is the maximum duration of the lock when acquired (after this, the lock will be considered as automatically released)
- the "wait" param (in seconds), which is the maximum duration to wait before acquiring the lock (after this, the client gives up about acquiring the lock)

If the lock is acquired, the system returns the lock as a **unique** URL.

## API

The HTTP API is fully described in the [the specific API.md file](API.md).

## Example of consuming the API

This example is described here with [the python/request library][REQUESTS] but it's a HTTP/RESTful API, so it's not linked with a specific language or tool. 

You can also have a look at a pure python client : [rdlm-py](https://github.com/thefab/rdlm-py).

### Imports and constants

    >>> import requests
    >>> import json

    >>> BASE_URL = "http://localhost:8888"
    >>> RESOURCE_NAME1 = "resource1"

### Acquire a lock on the resource "resource1" (and get it !)

    >>> lock_dict = {"title": "just an indicative client title", "lifetime": 300, "wait": 20}
    >>> raw_body = json.dumps(lock_dict)
    => you have to do an HTTP/POST with a non encoded body (raw) which is a JSON string with these 3 keys

    >>> r = requests.post("%s/locks/%s" % (BASE_URL, RESOURCE_NAME1), data=raw_body)
    => we post it to /locks/resource1

    >>> r.status_code
    201
    => SUCCESS / CREATED

    >>> lock_url = r.headers['Location']
    >>> lock_url
    http://localhost:8888/locks/resource1/ff14608f6ab342f0bb2a86d551d42a8c
    => the lock_url is the unique identifier for this successful lock

### Acquire a lock on the resource "resource1" (and don't get it, timeout after 20 ("wait") seconds)

    >>> lock_dict = {"title": "just an indicative client title", "lifetime": 300, "wait": 20}
    >>> raw_body = json.dumps(lock_dict)
    >>> r = requests.post("%s/locks/%s" % (BASE_URL, RESOURCE_NAME1), data=raw_body)
    >>> [...] blocking during 20 ("wait") seconds
    >>> r.status_code
    408
    => CLIENT ERROR / REQUEST TIMEOUT

### Release a lock (which is really exist !)

    >>> r = requests.delete(lock_url)
    >>> r.status_code
    204
    => SUCCESS / NO CONTENT (the lock is deleted)

### Release a lock (which is does not exist anymore !)

    >>> r = requests.delete(lock_url)
    >>> r.status_code
    404
    => CLIENT ERROR / NOT FOUND

# License (MIT)

    Copyright (C) 2013 Fabien MARTY <fabien.marty@gmail.com>
    
    Permission is hereby granted, free of charge, to any person obtaining a 
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, 
    and/or sell copies of the Software, and to permit persons to whom the 
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
    DEALINGS IN THE SOFTWARE.

[REQUESTS]: http://python-requests.org "python requests website"
[TORNADO]: http://www.tornadoweb.org/ "tornado website"
