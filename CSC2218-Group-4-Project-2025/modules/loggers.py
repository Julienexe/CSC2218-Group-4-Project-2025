import logging

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


# Logger as a Singleton
class LoggerSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls, name="FirebaseDB"):
        if cls._instance is None:
            cls._instance = Logger(name).get_logger()
        return cls._instance
