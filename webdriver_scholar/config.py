import configparser
import os
path = os.path.abspath(os.path.dirname(__file__))

config = configparser.ConfigParser()

config.read(os.path.join(path, 'config.ini'))

chrome_config = config['Chrome']

scihub_config = config['Scihub']

mode_config = config['Mode']

#print(dict(chrome_config))