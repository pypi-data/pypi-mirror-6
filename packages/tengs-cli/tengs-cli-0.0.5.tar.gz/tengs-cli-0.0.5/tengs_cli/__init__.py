import yaml

from settings import *

def generate_url(url, api_key=None):
    if api_key == None:
        api_key = value_for("api_key")
    return "{0}/api/{1}?api_key={2}".format(site, url, api_key)

def value_for(key):
    stream = file(file_path, 'r')
    return yaml.load(stream)[key]

def write_config(data):
    with open(file_path, 'w+') as outfile:
        outfile.write(yaml.dump(data, default_flow_style=False))
