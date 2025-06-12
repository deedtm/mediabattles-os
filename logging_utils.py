import logging
    
    
logging.basicConfig(level=logging.INFO)
    
    
def disable_logging(*names: str):
    names_str = ', '.join(names)
    logging.info(f'Disabling {names_str} logging...')
    
    for name, logger in logging.root.manager.loggerDict.items():
        if name.startswith(names) and isinstance(logger, logging.Logger):
            logging.info(f"Disabled {name}")
            logger.setLevel(logging.WARNING)
    
    logging.info('Logging was disabled')
