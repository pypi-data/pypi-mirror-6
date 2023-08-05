###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import

from setuptools import setup
from distutils import log


import sys
PY3 = sys.version_info.major > 2
if PY3:
   log.info("Python 3 detected.")
else:
   log.info("Python 2 detected.")


LONGSDESC = """
Autobahn|Python provides implementations of

 * The WebSocket Protocol
 * The Web Application Messaging Protocol (WAMP)

for Twisted and Asyncio.

More information:

 * https://github.com/tavendo/AutobahnPython
 * http://autobahn.ws/python
 * http://wamp.ws
"""

## get version string from "autobahn/__init__.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahn/__init__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


## Autobahn core packages
##
packages = ['autobahn',
            'autobahn.wamp2',
            'autobahn.websocket']


## Twisted integration
##
try:
   from twisted.internet import reactor
except:
   log.warn("Twisted not installed - skipping Twisted support packages")
   HAS_TWISTED = False
else:
   log.info("Twisted detected - installing Autobahn/Twisted integration")
   packages.append('autobahn.twisted')
   packages.append('twisted.plugins')
   HAS_TWISTED = True


## Asyncio integration
##
if PY3:
   try:
      from asyncio import Future
   except:
      log.warn("Asyncio not available - skipping Asyncio support packages")
   else:
      log.info("Asyncio detected - installing Autobahn/Asyncio integration")
      packages.append('autobahn.asyncio')
else:
   log.warn("Python 2 detected - skipping Autobahn/Asyncio integration")


## Now install Autobahn ..
##
setup(
   name = 'autobahn',
   version = verstr,
   description = 'Autobahn|Python provides WebSocket and WAMP for Twisted and Asyncio',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/python',
   platforms = ('Any'),
   install_requires = ['setuptools', 'zope.interface>=4.0.2'],
   extras_require = {
      ## this is ONLY needed on Python 3.3. Python 3.4+ has that integrated already!
      'asyncio': ["asyncio>=0.2.1"],

      ## you need Twisted for Autobahn/Twisted - obviously
      'twisted': ["twisted>=11.1"],

      ## native WebSocket and JSON acceleration: this should ONLY be used on CPython
      'accelerate': ["wsaccel>=0.6.2", "ujson>=1.33"],

      ## for (non-standard) WebSocket compression methods - not needed if you
      ## only want standard WebSocket compression ("permessage-deflate")
      'compress': ["python-snappy>=0.5", "lz4>=0.2.1"],

      ## needed if you want WAMPv2 binary serialization support
      'binary': ["msgpack-python>=0.4.0"]
   },
   packages = packages,
   zip_safe = False,
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Libraries"],
   keywords = 'autobahn autobahn.ws websocket realtime rfc6455 wamp rpc pubsub twisted asyncio'
)


if HAS_TWISTED:
   # Make Twisted regenerate the dropin.cache, if possible. This is necessary
   # because in a site-wide install, dropin.cache cannot be rewritten by
   # normal users.
   try:
      from twisted.plugin import IPlugin, getPlugins
      list(getPlugins(IPlugin))
   except Exception as e:
      log.warn("Failed to update Twisted plugin cache: {}".format(e))
   else:
      log.info("Twisted dropin.cache regenerated.")

   ## verify that Autobahn Twisted endpoints have been installed
   try:
      from twisted.internet.interfaces import IStreamServerEndpointStringParser
      from twisted.internet.interfaces import IStreamClientEndpointStringParser

      has_server_endpoint = False
      for plugin in getPlugins(IStreamServerEndpointStringParser):
         if plugin.prefix == "autobahn":
            has_server_endpoint = True
            break

      if has_server_endpoint:
         log.info("Autobahn Twisted stream server endpoint successfully installed")
      else:
         log.warn("Autobahn Twisted stream server endpoint installation seems to have failed")

      has_client_endpoint = False
      for plugin in getPlugins(IStreamClientEndpointStringParser):
         if plugin.prefix == "autobahn":
            has_client_endpoint = True
            break

      if has_client_endpoint:
         log.info("Autobahn Twisted stream client endpoint successfully installed")
      else:
         log.warn("Autobahn Twisted stream client endpoint installation seems to have failed")

   except:
      log.warn("Autobahn Twisted endpoint installation could not be verified")
