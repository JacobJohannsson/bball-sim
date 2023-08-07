import os
import sys
from .generate_game import generate_game_complex
from . import INSTALL_PATH
import json

##########################################################################################################################
#                                                  Display Probabilities                                                 #
##########################################################################################################################

def display_probabilities(probability_path):

    with open("{}/stats.txt".format(probability_path), 'r') as file:
        for line in file.readlines():
            print(line, end="")

##########################################################################################################################
#                                                    Game Probabilities                                                  #
##########################################################################################################################

def game_probability(home_team, away_team, games, initial_condition="None"):
    
    # we want to simulate 1000 games, keep track of average statistics
    
    # Construct the absolute path to the JSON file
    config_path = INSTALL_PATH + "/config_files/nba"

    with open("{}/game.json".format(config_path), "r") as file:
        game_settings = json.load(file)

    session_name = "{} @ {}".format(away_team, home_team)
    
    stats_dict = {
        home_team: {
            "Games": 0, 
            "Wins": 0, 
            "PTS": 0, 
            "REB": 0, 
            "DREB": 0, 
            "OREB": 0, 
            "TOV": 0, 
            "FGM": 0, 
            "FGA": 0, 
            "2PM": 0,
            "2PA": 0,
            "3PM": 0,
            "3PA": 0,
            "FTM": 0,
            "FTA": 0
        }, 
        away_team: {
            "Games": 0, 
            "Wins": 0, 
            "PTS": 0, 
            "REB": 0, 
            "DREB": 0, 
            "OREB": 0, 
            "TOV": 0, 
            "FGM": 0, 
            "FGA": 0, 
            "2PM": 0,
            "2PA": 0,
            "3PM": 0,
            "3PA": 0,
            "FTM": 0,
            "FTA": 0
        }
    }
    
    for i in range(games):
    
        # get new directory
        if os.path.exists("{}/results/nba/nba_games/prob_temp".format(INSTALL_PATH)):
            for file in os.listdir("{}/results/nba/nba_games/prob_temp".format(INSTALL_PATH)):
                os.remove("{}/results/nba/nba_games/prob_temp/{}".format(INSTALL_PATH, file))
            os.rmdir("{}/results/nba/nba_games/prob_temp".format(INSTALL_PATH))

        # generate game
        generate_game_complex(
            game_path = "{}/results/nba/nba_games/prob_temp".format(INSTALL_PATH),
            year = game_settings["year"],
            team1 = home_team, 
            team2 = away_team, 
            team1_home = True, 
            initial_condition = initial_condition, 
            q_length = 60 * game_settings["q_minutes"], 
            ot_length = 60 * game_settings["ot_minutes"]
        )

        # get stats
        with open("{}/results/nba/nba_games/prob_temp/stats.txt".format(INSTALL_PATH), 'r') as file:
            
            current_team = ""
            game_score_dict = {home_team: 0, away_team: 0}
            for line in file.readlines():
                
                if len(line) > 2:
                
                    if line.split(" ")[1] == "Stats":
                        current_team = line.split(" ")[0]

                    else:
                        stat = line.split(" ")[0][:-1]
                        if stat in ["PTS", "REB", "DREB", "OREB", "TOV"]:
                            stats_dict[current_team][stat] += int(line.split(" ")[1])
                            if stat == "PTS":
                                game_score_dict[current_team] = int(line.split(" ")[1])
                                

                        else:
                            stat_made = stat + "M"
                            stat_attempted = stat + "A"
                            stats_dict[current_team][stat_made] += int(line.split(" ")[1][:-1].split("/")[0])
                            stats_dict[current_team][stat_attempted] += int(line.split(" ")[1][:-1].split("/")[1])
            
            stats_dict[home_team]["Games"] += 1
            stats_dict[away_team]["Games"] += 1
            
            if game_score_dict[home_team] > game_score_dict[away_team]:
                stats_dict[home_team]["Wins"] += 1
            else:
                stats_dict[away_team]["Wins"] += 1
            
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        sys.stdout.write("\rSimulating {}... Currently on game: {}".format(session_name, i+1))
        sys.stdout.flush()
        
    # remove created directory for temp games
    for file in os.listdir("{}/results/nba/nba_games/prob_temp".format(INSTALL_PATH)):
        os.remove("{}/results/nba/nba_games/prob_temp/{}".format(INSTALL_PATH, file))
    os.rmdir("{}/results/nba/nba_games/prob_temp".format(INSTALL_PATH))

    print("\nCompiling Results...\n")

    # get new directory for probabilities
    if os.path.exists("{}/results/nba/nba_probabilities/{}".format(INSTALL_PATH, session_name)):
        for file in os.listdir("{}/results/nba/nba_probabilities/{}".format(INSTALL_PATH, session_name)):
            os.remove("{}/results/nba/nba_probabilities/{}/{}".format(INSTALL_PATH, session_name, file))
        os.rmdir("{}/results/nba/nba_probabilities/{}".format(INSTALL_PATH, session_name))
        
    os.mkdir("{}/results/nba/nba_probabilities/{}".format(INSTALL_PATH, session_name))
    
    
    with open("{}/results/nba/nba_probabilities/{}/stats.txt".format(INSTALL_PATH, session_name), 'w') as file:
            
        for team in [home_team, away_team]:
            
            if team == home_team:
                file.write("{} ({} Team) Average Stats\n".format(team, "Home"))
            else:
                file.write("{} ({} Team) Average Stats\n".format(team, "Away"))
            file.write("\n")
            
            file.write("Number of Games: {}\n".format(stats_dict[team]["Games"]))
            file.write("Win Probability: {}%\n".format(round(100 * stats_dict[team]["Wins"] / stats_dict[team]["Games"], 2)))
            file.write("\n")
            
            for stat in ["PTS", "REB", "DREB", "OREB", "TOV"]:
                file.write("{}: {}\n".format(stat, round(stats_dict[team][stat] / stats_dict[team]["Games"], 1)))
            
            for stat in ["FG", "2P", "3P", "FT"]:
                made_per_game = stats_dict[team][stat + "M"] / stats_dict[team]["Games"]
                attempted_per_game = stats_dict[team][stat + "A"] / stats_dict[team]["Games"]
                
                file.write("{}: {}/{}, {}%\n".format(stat, round(made_per_game, 1), round(attempted_per_game, 1), round(100 * made_per_game / attempted_per_game, 1)))
              
            file.write("\n")
    
    display_probabilities("{}/results/nba/nba_probabilities/{}".format(INSTALL_PATH, session_name))