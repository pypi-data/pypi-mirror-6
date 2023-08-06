import os
from os.path import expanduser

site = os.getenv('SITE', "http://tengs.ru")
home = expanduser("~")
file_path = "{0}/.tengs".format(home)
tengs_path = "{0}/tengs".format(home)
