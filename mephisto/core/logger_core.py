import logging

loggers = {}


def my_logger(name, verbose=True, log_file=None, level="info"):
    '''
    Gets the logger corresponds to each module
            Parameters:
                    name (string): the module name (__name__).
                    verbose (bool): INFO level activated if True.
                    log_file (string): path for saving logs locally.
                    level (string): logging level. Values options: [info, debug, warning, error, critical].

            Returns:
                    logger (logging.Logger): the corresponding logger to the given module name.
    '''

    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)

        level_dict = {"info": logging.INFO,
                      "debug": logging.DEBUG,
                      "warning": logging.WARNING,
                      "error": logging.ERROR,
                      "critical": logging.CRITICAL}

        logger.setLevel(logging.INFO if verbose else logging.DEBUG)
        logger.setLevel(level_dict[level.lower()])
        if log_file is None:
            handler = logging.StreamHandler()
        else:
            handler = logging.RotatingFileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - In module: %(name)s - %(levelname)-10s %(message)s')

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers[name] = logger
        return logger