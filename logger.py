import logging

logging.basicConfig(level=logging.INFO, filename="out.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

def log_info(message):
    logging.info(message)


def log_error(message):
    logging.error(message)