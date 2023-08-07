import os
from . import INSTALL_PATH

##########################################################################################################################
#                                                Display basement games                                                  #
##########################################################################################################################


def list_basement_games():
    
    for dir in os.listdir("{}/results/basement_games".format(INSTALL_PATH)):
        print("---{}---".format(dir))
        for file in os.listdir("{}/results/basement_games/{}".format(INSTALL_PATH, dir)):
            print("\t{} --> display with path: {}/{}".format(file, dir, file))
        print()