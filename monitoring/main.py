import argparse
import configparser
import multiprocessing

from typing import List

from process import MainProcess

def get_camera_configs(config_parser: configparser.ConfigParser) -> List[configparser.ConfigParser]:
    camera_configs: List[configparser.ConfigParser] = []

    for section in config_parser.sections():
        if section.startswith("camera"):
            camera_configs.append(config_parser[section])

    return camera_configs

if __name__ == "__main__":
    multiprocessing.freeze_support()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--config", default = 'config/homecage.conf')
    args = arg_parser.parse_args()

    config_parser = configparser.ConfigParser()
    config_parser.read(args.config)

    host_config = config_parser["host"]
    camera_configs = get_camera_configs(config_parser)

    main = MainProcess(host_config=host_config, camera_configs=camera_configs)
    main.start()

    while(True):
        pass
