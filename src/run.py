from config import Config


def main():
    cfg = Config.from_yaml()
    # Only adding 'server' means we are in backup mode
    if any([True for _, settings in cfg.cfg.items() if list(settings.keys()) == ['server']]):
        current_config = Config.from_current(cfg.cfg)
        current_config.to_file()
        print('Backed-up current configurations')
        return

    cfg.apply()
    print('Finished applying configurations')


if __name__ == "__main__":
    main()
