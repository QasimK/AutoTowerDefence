'''
Created on 16 Jul 2012

@author: Qasim

Run a single village.
'''

import sys
import os.path
import logging

import atd_bot
import dna

_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

V_LOC = os.path.join(_BASE_PATH, "atd_data", "village.txt")
PLANET_LOC = os.path.join(_BASE_PATH, "atd_data", "planet.txt")
LOGS_LOC = os.path.join(_BASE_PATH, "atd_data", "logs")

def setup_logging():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    
    simple_formatter = logging.Formatter('%(levelname)-8s: %(message)s')
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(simple_formatter)
    logger.addHandler(console)
    
    full_format = logging.Formatter('%(levelname)-8s:%(asctime)s:%(message)s',
                                       datefmt="%H:%M:%S")

    error_logfile = os.path.join(LOGS_LOC, "log-errors.txt")
    error = logging.FileHandler(error_logfile, 'w')
    error.setLevel(logging.WARNING)
    error.setFormatter(full_format)
    logger.addHandler(error)

    normal_logfile = os.path.join(LOGS_LOC, "log.txt")
    normal = logging.FileHandler(normal_logfile, 'w')
    normal.setLevel(logging.DEBUG)
    normal.setFormatter(full_format)
    logger.addHandler(normal)
    
    all_logfile = os.path.join(LOGS_LOC, "log-info.txt")
    all_log = logging.FileHandler(all_logfile, 'w')
    all_log.setLevel(logging.INFO)
    all_log.setFormatter(full_format)
    logger.addHandler(all_log)
    

def main():
    setup_logging()
    logging.info("Setting up a village run.")
    
    planet = dna.PlanetFile(PLANET_LOC)
    logging.debug("Loaded Planet File")
    
    village = dna.VillageFile(V_LOC, planet, atd_bot.score_func)
    logging.info("Loaded Village File:\n"+str(village))
    
    next_develops = False
    while True:
        if next_develops:
            logging.info("NEXT Step will develop village.")
        if not village.step():
            next_develops = True
        else:
            next_develops = False
        logging.info("Village is now:\n"+str(village))
    
    logging.info("The village run has ended.")
    logging.shutdown()

if __name__ == '__main__':
    main()
