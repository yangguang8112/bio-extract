import configparser

config = configparser.ConfigParser()

config.read('config.ini')

chrome_config = config['Chrome']

#print(dict(chrome_config))