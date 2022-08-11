from config import Config

cfg = Config.from_yaml('test-cfg.yml')
cfg.apply()

print('Finished applying configurations')
