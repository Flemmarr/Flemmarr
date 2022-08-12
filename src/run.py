from config import Config

cfg = Config.from_yaml('test-cfg2.yml')
cfg.apply()

print('Finished applying configurations')
