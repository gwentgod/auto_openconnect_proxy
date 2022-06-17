import logging

LOG_FORMAT = '%(asctime)s: %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def parse_file(path, item_count):
    try:
        with open(path) as target_file:
            content = target_file.read().split('\n')
            if len(content) < item_count:
                logging.critical('Failed parsing mail credentials')
                exit(1)

            return content[:item_count]
    except FileNotFoundError:
        logging.critical('Cannot find mail credentials')
        exit(1)
