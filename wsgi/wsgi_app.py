#!/usr/bin/python
import logging
import os
import sys

from werkzeug.debug import DebuggedApplication

logging.basicConfig(
  level=logging.DEBUG,
  format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)

(file_path, fname) = os.path.split(__file__)
app_path = os.path.dirname(file_path)
os.chdir(app_path)
logging.info("My path is " + app_path)
sys.path.insert (0, app_path)

namespace_dir = os.path.join(app_path, '..')
all_repos = ['vedavaapi_core', 'ullekhanam', 'docimage', 'vedavaapi_api', 'sling']
for repo in all_repos:
  sys.path.insert(1, os.path.join(namespace_dir, repo))


sys.stdout = sys.stderr
from vedavaapi import run

application = DebuggedApplication(run.app, True)
