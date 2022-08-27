from config import Config
from constants import Service


if __name__ == "__main__":
    cfg = Config.from_current('radarr', 'http://192.168.178.47', 7878)
    cfg.to_file('radarr-test.yml')


    # cfg = Config.from_yaml('test-cfg2.yml')
    # cfg.apply()
    #
    # print('Finished applying configurations')
