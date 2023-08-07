from . import INSTALL_PATH
import json

##########################################################################################################################
#                                                  Data Initialization                                                   #
##########################################################################################################################

all_q = []
q_start_dict = {}
q_end_dict = {}
bonus_amount = {}
team_colours = {}

def get_dicts(num_ot=20, q_length=12*60, ot_length=5*60):
    # get global all_q list, q_start, q_end and bonus_amount dicts

    global all_q, q_start_dict, q_end_dict, bonus_amount
    
    all_q = ["q1", "q2", "q3", "q4"]
    
    q_start_dict = {
        "q1": 0, 
        "q2": 1*q_length, 
        "q3": 2*q_length, 
        "q4": 3*q_length
    }

    q_end_dict = {
        "q1": 1*q_length, 
        "q2": 2*q_length, 
        "q3": 3*q_length, 
        "q4": 4*q_length
    }
    
    bonus_amount = {
        "q1": 4, 
        "q2": 4, 
        "q3": 4, 
        "q4": 4        
    }
    
    for i in range(num_ot):
        all_q.append("ot" + str(i+1))
        q_start_dict["ot" + str(i+1)] = 4 * q_length + i * ot_length
        q_end_dict["ot" + str(i+1)] = 4 * q_length + (i+1) * ot_length
        bonus_amount["ot" + str(i+1)] = 3

def get_colours(year="2022-23"):
    # get global team_colours dictionary form files

    global team_colours
    team_colours = {}
    with open("{}/data_files/team_colours/{}colours.txt".format(INSTALL_PATH, year), 'r') as file:
        file.readline()
        for line in file.readlines():
            team_colours[line.split(" ")[0]] = []
            
            for colour in line.split(" ")[1:]:
                team_colours[line.split(" ")[0]].append(colour)

def assign_colours(team1, team2):
    # assign team colours based on the two teams (make sure no two teams have the same colour)
    colour1 = team_colours[team1][0]
    colour2 = team_colours[team2][0]
    
    if colour1 == colour2:
        if len(team_colours[team1]) > len(team_colours[team2]):
            colour1 = team_colours[team1][1]
        else:
            colour2 = team_colours[team2][1]
    
    return colour1, colour2

def initialize(nba):

    if nba:
        # with open("{}/config_files/nba/game.json".format(INSTALL_PATH), 'r') as file:
            # game_config = json.load(file)
            # q_length = 60 * game_config["q_minutes"]
            # ot_length = 60 * game_config["ot_minutes"]
        # get_dicts(q_length=q_length, ot_length=ot_length)
        get_dicts()

        #need to find a way to replace this year argument with something better
        get_colours("2022-23")
    else:
        with open("{}/config_files/basement/game.json".format(INSTALL_PATH), 'r') as file:
            game_config = json.load(file)
            q_length = 60 * game_config["q_minutes"]
            ot_length = 60 * game_config["ot_minutes"]
        get_dicts(q_length=q_length, ot_length=ot_length)
    
    print(all_q)