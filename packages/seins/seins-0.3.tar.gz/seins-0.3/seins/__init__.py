__author__ = 'mackaiver'

from colorama import init, Fore, Style
#init colorama so it works on windows as well.
#The autoreset flag keeps me from using RESET on each line I want to color
init(autoreset=True)

import logging
#create a logger for this module
logger = logging.getLogger(__name__)
#use colorama codes to color diferent output levels
logging.addLevelName(logging.INFO, Style.BRIGHT +
                                      logging.getLevelName(logging.INFO) + Style.RESET_ALL)
logging.addLevelName(logging.WARNING, Style.BRIGHT + Fore.YELLOW +
                                      logging.getLevelName(logging.WARNING) + Style.RESET_ALL)
logging.addLevelName(logging.ERROR, Style.BRIGHT + Fore.RED + logging.getLevelName(logging.ERROR) + Style.RESET_ALL)
#the usual formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# create a handler and make it use the formatter
handler = logging.StreamHandler()
handler.setFormatter(formatter)
# now tell the logger to use the handler
logger.addHandler(handler)
logger.propagate = False