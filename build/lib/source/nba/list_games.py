import os
from . import INSTALL_PATH

##########################################################################################################################
#                                                    Formatting Dict                                                     #
##########################################################################################################################

def get_month_dict():
    global month_dict

    month_dict = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

def get_query_information(nba_games, nba_playoffs, nba_seasons):
    global query_information

    query_information = {
        "nba_games": nba_games,
        "nba_seasons": nba_seasons,
        "nba_playoffs": nba_playoffs,
        "nba_probabilities": False
    }

def initialize(nba_games, nba_seasons, nba_playoffs):
    get_month_dict()
    get_query_information(nba_games, nba_seasons, nba_playoffs)

##########################################################################################################################
#                                                Display basement games                                                  #
##########################################################################################################################


def list_nba_games(nba_games=False, nba_playoffs=False, nba_seasons=False):

    initialize(nba_games, nba_seasons, nba_playoffs)

    for sim_type in os.listdir("{}/results/nba".format(INSTALL_PATH)):

        if query_information[sim_type] == True:
            print("---{}---".format(sim_type))

            if sim_type == "nba_games":
                for game in os.listdir("{}/results/nba/{}".format(INSTALL_PATH, sim_type)):
                    print("\t{} --> display with path: {}/{}".format(game, sim_type, game))
            
            elif sim_type == "nba_seasons":
                for season in os.listdir("{}/results/nba/{}".format(INSTALL_PATH, sim_type)):
                    print("\t---{}---".format(season))
                    for month in os.listdir("{}/results/nba/{}/{}".format(INSTALL_PATH, sim_type, season)):
                        if month in month_dict:
                            print("\t\t---{}---".format(month_dict[month]))
                            for game in os.listdir("{}/results/nba/{}/{}/{}".format(INSTALL_PATH, sim_type, season, month)):
                                print("\t{} --> display with path: {}/{}/{}/{}".format(game, sim_type, season, month, game))
                        else:
                            print("\t\t---{}---".format(month))
                            for series in os.listdir("{}/results/nba/{}/{}/{}".format(INSTALL_PATH, sim_type, season, month)):
                                print("\t\t\t---{}---".format(series))
                                for game in os.listdir("{}/results/nba/{}/{}/{}/{}".format(INSTALL_PATH, sim_type, season, month, series)):
                                    print("\t{} --> display with path: {}/{}/{}/{}/{}".format(game, sim_type, season, month, series, game))
            
            elif sim_type == "nba_playoffs":
                print("none")