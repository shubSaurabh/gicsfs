# logger.py
import logging

class Logger:
    def __init__(self, log_file):
        self.logger = logging.getLogger("SecureFileStorage")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
