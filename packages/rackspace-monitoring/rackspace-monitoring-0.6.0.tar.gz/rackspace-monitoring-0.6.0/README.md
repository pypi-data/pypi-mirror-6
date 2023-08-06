# rackspace-monitoring

rackspace-monitoring is a Python client library for Rackspace Cloud Monitoring
built on top of [Apache Libcloud](http://libcloud.apache.org).

# Installation

Library can be installed using `pip`:

```bash
pip install rackspace-monitoring
```

# Usage

```python
from pprint import pprint

from rackspace_monitoring.providers import get_driver
from rackspace_monitoring.types import Provider

Cls = get_driver(Provider.RACKSPACE)
driver = Cls('username', 'api key')
pprint(driver.list_entities())
```

# Certificate verification

Libcloud verifies server SSL certificate by default. This means you need to
have the correct CA certificate files installed on your computer for this
library to work.

If Libcloud cannot find CA certificate files, you will see an error similar to
the one below:

`"RuntimeError: No CA Certificates were found in CA_CERTS_PATH."`

This can be addressed by installing the CA certificate files. Below you can
find the names of the packages which include CA certificate files.

* **openssl** on CentOS/Fedora (yum)
* **ca-certificates** on Debian/Ubuntu/Arch/Gentoo (apt-get)
* **ca_root_nss** on FreeBSD (ports)
* **curl-ca-bundle** on Mac OS X (ports)

# Testing, style, code coverage

## Running tests

`sudo tox`

This will run tests on all the supported versions.

If you only want to run tests for a single version use:

`sudo tox -e <version>`

Where version is one of:

* py25
* py26
* py27
* pypy
* py32

## Checking pep8 compliance

`python setup.py pep8`

## Generating code coverage report

`python setup.py coverage`

# Build status

[![Build Status](https://secure.travis-ci.org/racker/rackspace-monitoring.png)](http://travis-ci.org/racker/rackspace-monitoring)

# Issues, Feedback

Please use Github issue tracker or send an email to `monitoring@rackspace.com`.
