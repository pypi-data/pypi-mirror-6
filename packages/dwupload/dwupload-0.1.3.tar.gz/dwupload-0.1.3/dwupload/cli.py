import argparse


def process_arguments():
    parser = argparse.ArgumentParser(prog="dwupload", description="Demandware Upload File System Watcher")
    parser.add_argument("watch_path", nargs="?")
    parser.add_argument("-c", "--config", dest="config_path")

    args = parser.parse_args()
    return args