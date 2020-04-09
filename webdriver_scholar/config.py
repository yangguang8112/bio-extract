import configparser

config = configparser.ConfigParser()

config.read('config.ini')

chrome_config = config['Chrome']

scihub_config = config['Scihub']

#print(dict(chrome_config))