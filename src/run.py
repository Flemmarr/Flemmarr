from config import Config

cfg = Config.from_yaml()
cfg.apply()

print('Finished applying configurations')
