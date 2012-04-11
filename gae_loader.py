"""

Some code borrow from http://code.google.com/p/google-app-engine-django/

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
import code
import getpass
import logging

import sys, os

APP_ID = None

project_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = "packages"
package_dir_path = os.path.join(os.path.dirname(__file__), package_dir)

# Allow unzipped packages to be imported
# from packages folder
sys.path.insert(0, package_dir_path)
sys.path.insert(1, os.path.join(project_dir, "apps"))
sys.path.insert(2, os.path.join(project_dir, "libs"))

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

# Append zip archives to path for zipimport
if os.path.exists(package_dir_path):
  for filename in os.listdir(package_dir_path):
    if filename.endswith((".zip", ".egg")):
      sys.path.insert(3, "%s/%s" % (package_dir_path, filename))

def load_sdk():
  # Try to import the appengine code from the system path.
  try:
    from google.appengine.api import apiproxy_stub_map
  except ImportError, e:
    # Hack to fix reports of import errors on Ubuntu 9.10.
    if 'google' in sys.modules:
      del sys.modules['google']
    # Not on the system path. Build a list of alternative paths where it may be.
    # First look within the project for a local copy, then look for where the Mac
    # OS SDK installs it.
    paths = [os.path.join(project_dir, '.google_appengine'),
             os.path.join(project_dir, 'google_appengine'),
             '/usr/local/google_appengine']
    # Then if on windows, look for where the Windows SDK installed it.
    for path in os.environ.get('PATH', '').split(';'):
      path = path.rstrip('\\')
      if path.endswith('google_appengine'):
        paths.append(path)
    try:
      from win32com.shell import shell
      from win32com.shell import shellcon
      id_list = shell.SHGetSpecialFolderLocation(
          0, shellcon.CSIDL_PROGRAM_FILES)
      program_files = shell.SHGetPathFromIDList(id_list)
      paths.append(os.path.join(program_files, 'Google',
                                'google_appengine'))
    except ImportError, e:
      # Not windows.
      pass
    # Loop through all possible paths and look for the SDK dir.
    SDK_PATH = None
    for sdk_path in paths:
      if os.path.exists(sdk_path):
        SDK_PATH = os.path.realpath(sdk_path)
        break
    if SDK_PATH is None:
      # The SDK could not be found in any known location.
      sys.stderr.write("The Google App Engine SDK could not be found!\n")
      sys.stderr.write("See README for installation instructions.\n")
      sys.exit(1)
    if SDK_PATH == os.path.join(project_dir, 'google_appengine'):
      logging.warn('Loading the SDK from the \'google_appengine\' subdirectory '
                   'is now deprecated!')
      logging.warn('Please move the SDK to a subdirectory named '
                   '\'.google_appengine\' instead.')
      logging.warn('See README for further details.')
    # Add the SDK and the libraries within it to the system path.
    EXTRA_PATHS = [
        SDK_PATH,
        os.path.join(SDK_PATH, 'lib', 'antlr3'),
        os.path.join(SDK_PATH, 'lib', 'django_1_3'),
        os.path.join(SDK_PATH, 'lib', 'ipaddr'),
        os.path.join(SDK_PATH, 'lib', 'webob'),
	os.path.join(SDK_PATH, 'lib', 'webob_1_1_1'),
        os.path.join(SDK_PATH, 'lib', 'simplejson'),
        os.path.join(SDK_PATH, 'lib', 'whoosh'),
        os.path.join(SDK_PATH, 'lib', 'yaml', 'lib'),
        os.path.join(SDK_PATH, 'lib', 'fancy_urllib'),
    ]
    # Add SDK paths at the start of sys.path, but after the local directory which
    # was added to the start of sys.path on line 50 above. The local directory
    # must come first to allow the local imports to override the SDK and
    # site-packages directories.
    sys.path = sys.path[0:1] + EXTRA_PATHS + sys.path[1:]

def load_appengine_environment():
  """ Loads the appengine environment. """
  global APP_ID
  from google.appengine.api import yaml_errors
  from google.appengine.api import apiproxy_stub_map

  stub = apiproxy_stub_map.apiproxy.GetStub("datastore_v3")

  # Detect if we are running under an appserver.
  try:
    from google.appengine.tools import dev_appserver
    appconfig, unused_matcher, options = dev_appserver.LoadAppConfig(project_dir, {})
    APP_ID = appconfig.application
  except (ImportError, yaml_errors.EventListenerYAMLError), e:
    logging.warn("Could not read the Application ID from app.yaml. "
                 "This may break things in unusual ways!")
    # Something went wrong.
    APP_ID = "unknown"


def load_stubs():
  from google.appengine.tools import dev_appserver_main
  args = dev_appserver_main.DEFAULT_ARGS.copy()
  from google.appengine.tools import dev_appserver
  dev_appserver.SetupStubs(APP_ID, **args)

  logging.debug("Loading application '%s'" % (APP_ID))

def load_gae():
  load_sdk()
  load_appengine_environment()
  load_stubs()


