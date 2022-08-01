import yaml
from api import Api

configs = yaml.safe_load(open('./config/config.yml', 'r'))

for key in configs:
    config = configs[key]
    server = config['server']
    config.pop('server')

    api = Api(server['address'], server['port'])

    print('Trying to connect to {}'.format(key))
    api.initialize()

    print('Starting to apply configuration')
    api.apply(config)

print('Finished to apply configurations')
