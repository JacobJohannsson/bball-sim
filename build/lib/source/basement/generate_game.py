import numpy as np
import random
import json
import os
from scipy.stats import expon
from scipy.stats import poisson
from . import INSTALL_PATH

##########################################################################################################################
#                                                  Generate Game Wrapper                                                 #
##########################################################################################################################


def generate_game_simple(game_name):

    # Construct the absolute path to the JSON file
    config_path = INSTALL_PATH + "/config_files/basement"

    with open("{}/game.json".format(config_path), "r") as file:
        game_settings = json.load(file)
    
    with open("{}/team1.json".format(config_path), "r") as file:
        team1_settings = json.load(file)

    with open("{}/team2.json".format(config_path), "r") as file:
        team2_settings = json.load(file)

    print("Generating Game: {}...".format(game_name))

    generate_game(
        game_path = "{}/results/basement_games/generated_games/{}".format(INSTALL_PATH, game_name),
        q_length = 60 * game_settings["q_minutes"],
        ot_length = 60 * game_settings["ot_minutes"],
        team1 = team1_settings["name"], 
        team2 = team2_settings["name"], 
        pace = game_settings["pace"],
        skill1 = team1_settings["skill"],
        threefreq1 = team1_settings["threefreq"],
        skill2 = team2_settings["skill"],
        threefreq2 = team2_settings["threefreq"],
        three_penalty = game_settings["three_penalty"],
        tight_game = game_settings["tight_game"],
        randomness = game_settings["randomness"]
    )

    print("Successfully Generated Game: {} --> display with path: generated_games/{}".format(game_name, game_name))
    
    return "{}/results/basement_games/generated_games/{}".format(INSTALL_PATH, game_name)

##########################################################################################################################
#                                                  Data Initialization                                                   #
##########################################################################################################################

def get_dicts(num_ot=20, q_length=12*60, ot_length=5*60):
    # get global all_q list, q_start, q_end and bonus_amount dicts

    global all_q, q_start_dict, q_end_dict
    
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

def initialize(q_length, ot_length):
    get_dicts(q_length=q_length, ot_length=ot_length)

##########################################################################################################################
#                                                     Simulate Possession                                                #
##########################################################################################################################


def format_num(num):
    if num >= 10:
        return str(num)
    else:
        return str(num) + "  "

def format_seconds(seconds):
    if seconds <= 9:
        return "0{}".format(seconds)
    else:
        return "{}".format(seconds)
        
def format_time(q, q_length, ot_length, time):
    q_end_dict = {
                    "q1": 1*q_length, 
                    "q2": 2*q_length, 
                    "q3": 3*q_length, 
                    "q4": 4*q_length, 
                    "ot1": 4*q_length + 1*ot_length, 
                    "ot2": 4*q_length + 2*ot_length, 
                    "ot3": 4*q_length + 3*ot_length,
                    "ot4": 4*q_length + 4*ot_length
                   }
    time = q_end_dict[q] - time
    minutes = time // 60
    seconds = time % 60
    return "{}:{}".format(minutes, format_seconds(seconds))

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def next_point(time, score1, score2, 
               pace=24, skill1=1500, threefreq1=0.3, skill2=1500, threefreq2=0.3, 
               three_penalty=800, tight_game=100, randomness=0.5):
    
    # find the time at which a team scores
    offset1 = 8
    offset2 = poisson.rvs(offset1, 1)
    new_time = expon.rvs(offset2, pace-offset1, 1)[0]
    if new_time < 4:
        new_time = 4
    else:
        new_time = round(new_time, 0)
    
    # penalize team for shooting lots of threes
    skill1 += 3*(skill1-1500)*(1-randomness) - (three_penalty * threefreq1 + (score1-score2) * tight_game)
    skill2 += 3*(skill2-1500)*(1-randomness) - (three_penalty * threefreq2 + (score2-score1) * tight_game)
    
    scoring_dict1 = {
                    (0, threefreq1): 3, 
                    (threefreq1, 0.94): 2, 
                    (0.94, 0.99): 1, 
                    (0.99, 1.0): 4
                    }
    
    scoring_dict2 = {
                    (0, threefreq2): 3, 
                    (threefreq2, 0.94): 2, 
                    (0.94, 0.99): 1, 
                    (0.99, 1.0): 4
                    }
     
    # find who scores, and what point
    probabilities = softmax([skill1/(skill1+skill2), skill2/(skill1+skill2)])
    team_prob = random.uniform(0,1)
    basket_prob = random.uniform(0,1)
    
    if (team_prob < probabilities[0]):
        for basket in scoring_dict1:
            if basket_prob >= basket[0] and basket_prob  < basket[1]:
                return int(time+new_time), int(score1 + scoring_dict1[basket]), int(score2)
    else:
        for basket in scoring_dict2:
            if basket_prob >= basket[0] and basket_prob  < basket[1]:
                return int(time+new_time), int(score1), int(score2 + scoring_dict2[basket])
          
##########################################################################################################################
#                                                        Generate Game                                                   #
##########################################################################################################################


def generate_game(
    game_path, q_length, ot_length, team1, team2,
    pace=24, skill1=1500, threefreq1=0.3, skill2=1500, threefreq2=0.3, 
    three_penalty=800, tight_game=100, randomness=0.5
):
    
    initialize(q_length, ot_length)

    q_list = ["q1"]
    time = [0]
    score1 = [0]
    score2 = [0]
    
    # get through 4 quarters first
    
    for q in all_q[:4]:
        while (True):                
            new_time, new_score1, new_score2 = next_point(time[-1], score1[-1], score2[-1], pace, skill1, threefreq1, skill2, threefreq2, three_penalty, tight_game, randomness)
            if new_time > q_end_dict[q]:
                q_list.append(q)
                time.append(q_end_dict[q])
                score1.append(score1[-1])
                score2.append(score2[-1])
                break
            else:
                q_list.append(q)
                time.append(new_time)
                score1.append(new_score1)
                score2.append(new_score2)
    
    for q in all_q[4:]:
        if (score1[-1] != score2[-1]):
            break
        while (True):
            new_time, new_score1, new_score2 = next_point(time[-1], score1[-1], score2[-1], pace, skill1, threefreq1, skill2, threefreq2, three_penalty, tight_game, randomness)
            if new_time > q_end_dict[q]:
                q_list.append(q)
                time.append(q_end_dict[q])
                score1.append(score1[-1])
                score2.append(score2[-1])
                break
            else:
                q_list.append(q)
                time.append(new_time)
                score1.append(new_score1)
                score2.append(new_score2)
    
    # get new directory
    if os.path.exists(game_path):
        for file in os.listdir(game_path):
            os.remove("{}/{}".format(game_path, file))
        os.rmdir(game_path)
    os.mkdir(game_path)
    
    # create game log file
    open("{}/game_log.txt".format(game_path), 'w').close()

    with open("{}/game_log.txt".format(game_path), 'w') as file:
        file.write("q {}:00 ot {}:00\n".format(q_length // 60, ot_length // 60))
        file.write("{} {}\n".format(team1, team2))
        
        for i in range(0, len(time)):
            file.write("{} {} {}-{}\n".format(q_list[i], format_time(q_list[i], q_length, ot_length, time[i]), score1[i], score2[i]))