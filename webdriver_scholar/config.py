import configparser

config = configparser.ConfigParser()

config.read('config.ini')

chrome_config = config['Chrome']

scihub_config = config['Scihub']

mode_config = config['Mode']

#print(dict(chrome_config))