import logging

# custom log level 'OUT' which will be used to print the instruction sequence
OUT_LEVEL = 25
logging.addLevelName(OUT_LEVEL, "OUT")

def log_out(self, message, *args, **kwargs):
    if self.isEnabledFor(OUT_LEVEL):
        self._log(OUT_LEVEL, message, args, **kwargs)

logging.Logger.out = log_out


def setup():
    logger = logging.getLogger("pr5")
    logger.setLevel(logging.DEBUG)
    
    # logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # logging to a file
    file_handler = logging.FileHandler("sim.log", mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    # log format
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
