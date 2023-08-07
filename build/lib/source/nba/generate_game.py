from scipy.stats import expon
from scipy.stats import poisson
from scipy.stats import norm
import os
import random
from . import INSTALL_PATH
import json

##########################################################################################################################
#                                                Generate Game Wrapper                                                   #
##########################################################################################################################


def generate_single_game(home_team, away_team, initial_condition="None"):
    
    # Construct the absolute path to the JSON file
    config_path = INSTALL_PATH + "/config_files/nba"

    with open("{}/game.json".format(config_path), "r") as file:
        game_settings = json.load(file)

    game_name = "{} @ {}".format(away_team, home_team)
    
    print("Generating Game: {}...".format(game_name))
    
    generate_game_complex(
        game_path = "{}/results/nba/nba_games/{}".format(INSTALL_PATH, game_name),
        year = game_settings["year"],
        team1 = home_team, 
        team2 = away_team, 
        team1_home = True, 
        initial_condition = initial_condition, 
        q_length = 60 * game_settings["q_minutes"], 
        ot_length = 60 * game_settings["ot_minutes"]
    )

    print("Successfully Generated Game: {} --> display with path: nba_games/{}".format(game_name, game_name))

    return "{}/results/nba/nba_games/{}".format(INSTALL_PATH, game_name)

##########################################################################################################################
#                                                  Data Initialization                                                   #
##########################################################################################################################

def set_hyperparameters():
    
    ##################################################################
    
    global rush_multiplier_2pt, foul_multiplier_2pt, rush_multiplier_3pt, foul_multiplier_3pt
    
    rush_multiplier_2pt = 1
    foul_multiplier_2pt = 1

    rush_multiplier_3pt = 1
    foul_multiplier_3pt = 1
    
    ##################################################################
    
    global three_point_foul_scaling_factor
    
    three_point_foul_scaling_factor = 1
    
    ##################################################################
    
    global steal_turnover_multiplier
    
    steal_turnover_multiplier = 1
    
    ##################################################################
    
    global minimum_time_to_foul_or_TOV
    
    minimum_time_to_foul_or_TOV = 1.5 #seconds
    
    ##################################################################
    
    global shot_time_std_dev
    
    shot_time_std_dev = 1/1.75
    
    ##################################################################
    
    global mean_pf_floor_TOV_multiplier
    
    mean_pf_floor_TOV_multiplier = 0.5
    
    ##################################################################
    
    # free throws
    global free_throw_hot_effect, free_throw_cold_effect
    
    free_throw_hot_effect, free_throw_cold_effect = 0, 0
    
    # 2 point field goal
    global field_goal_2_hot_effect, field_goal_2_cold_effect
    
    field_goal_2_hot_effect, field_goal_2_cold_effect = 0, 0
    
    # 3 point field goal
    global field_goal_3_hot_effect, field_goal_3_cold_effect
    
    field_goal_3_hot_effect, field_goal_3_cold_effect = 0, 0
    
    
    ##################################################################    

def get_game_trackers(team1, team2):
    
    ##################################################################
    
    global tov_dict, reb_dict
    
    # keep track of turnovers
    tov_dict = {team1: 0, team2: 0}
    
    # keep track of rebounds
    reb_dict = {team1: {"def": 0, "off": 0}, team2: {"def": 0, "off": 0}}
    
    ##################################################################
    
    global two_pt_dict, three_pt_dict, free_throw_dict
    
    # keep track of 2pt makes and total shots
    two_pt_dict = {team1: [0,0], team2: [0,0]}
    
    # keep track of 3pt makes and total shots
    three_pt_dict = {team1: [0,0], team2: [0,0]}
    
    # keep track of free throw makes and total shots
    free_throw_dict = {team1: [0,0], team2: [0,0]}
    
    ##################################################################

def get_stats(year="2022-23"):
    global team_stats
    team_stats = {}

    with open("{}/data_files/team_stats/{}_team_stats.txt".format(INSTALL_PATH, year), "r") as file:
        headers = file.readline().strip().split(" ")
        for line in file.readlines():
            info = line.strip().split(" ")
            team_stats[info[0]] = {}
            for i in range(1, len(headers)):
                team_stats[info[0]][headers[i]] = float(info[i])
    
def get_dicts(num_ot=20, q_length=12*60, ot_length=5*60):
    
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

def initialize(team1, team2, q_length, ot_length, year):
    set_hyperparameters()
    get_game_trackers(team1=team1, team2=team2)
    get_stats(year=year)
    get_dicts(q_length=q_length, ot_length=ot_length)

##########################################################################################################################
#                                                       Formatting                                                       #
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
    time = q_end_dict[q] - time
    minutes = int(time // 60)
    seconds = int(time % 60)
    return "{}:{}".format(minutes, format_seconds(seconds))

def plural_fouls(defense_fouls):
    if defense_fouls == 1:
        return ""
    return "s"

##########################################################################################################################
#                                                  Possession Simulator                                                  #
##########################################################################################################################

            
def jump_ball(team1, team2):
    '''Returns which team wins the jump ball'''
    if random.uniform(0,1) <= 0.5:
        return team1, team2
    return team2, team1

def score_gap(offense_score, defense_score):
    '''Simply computes the score gap between offense and defense'''
    return offense_score - defense_score

def floor_foul_TOV(offense, defense, defense_rush): # fix pf_floor probability
    '''Takes in the current situation, and returns the chance of a foul on the floor'''

    # get chance_pf_floor
    
    chance_3pa = team_stats[offense]["3PA/PLAY"]
    chance_2pa = team_stats[offense]["FGA/PLAY"] - chance_3pa
    
    chance_pf = 1/2 * (team_stats[offense]["PFD/PLAY"] + team_stats[defense]["PF/PLAY"])
    chance_pf_2pt = team_stats[offense]["FTA/PLAY"] / (2 + chance_3pa / chance_2pa)
    chance_pf_3pt = chance_pf_2pt * chance_3pa / chance_2pa
    chance_pf_floor = chance_pf - chance_pf_2pt * (1 + chance_3pa / chance_2pa)
    
    # run pf_floor and turnover probabilities here

    turnover_probabilty = 1/(1 + steal_turnover_multiplier) * (team_stats[offense]["TOV/PLAY"] + steal_turnover_multiplier * team_stats[defense]["STL/PLAY"])
    
    if defense_rush:
        non_shot_probability_dict = {
            (0, 2 * turnover_probabilty): (False, True),
            (2 * turnover_probabilty, 1): (True, False)
        }
    else:
        non_shot_probability_dict = {
            (0, chance_pf_floor): (True, False),
            (chance_pf_floor, chance_pf_floor + turnover_probabilty): (False, True),
            (chance_pf_floor + turnover_probabilty, 1): (False, False)
        }    

    random_num = random.uniform(0,1)
    
    # assign these probabilities now
    
    for prob_range in non_shot_probability_dict:
        if random_num > prob_range[0] and random_num < prob_range[1]:
            return non_shot_probability_dict[prob_range] 
            # pf_floor, turnover
    
def type_of_shot(offense, defense, need_three):
    '''Takes in the offense and defense, and returns the type of shot generated, given that a shot was attempted'''
    
    if need_three:
        return "three"
    
    chance_3pa = team_stats[offense]["3PA/PLAY"]
    chance_2pa = team_stats[offense]["FGA/PLAY"] - chance_3pa
    
    probability = chance_3pa / (chance_3pa + chance_2pa)
    
    type_of_shot_probability_dict = {
        (0, probability): "three",
        (probability, 1): "two"
    }
    
    random_num = random.uniform(0,1)

    for prob_range in type_of_shot_probability_dict:
        if random_num > prob_range[0] and random_num < prob_range[1]:
            return type_of_shot_probability_dict[prob_range]
            # "two" or "three"
    
def shooting_foul(offense, defense, rush, shot_type):
    '''Returns whether or not a foul was commited on the play'''
    
    # get the chance of commiting a foul during shooting
    
    chance_3pa = team_stats[offense]["3PA/PLAY"]
    chance_2pa = team_stats[offense]["FGA/PLAY"] - chance_3pa
    
    chance_pf_2pt = team_stats[offense]["FTA/PLAY"] / (2 + chance_3pa / chance_2pa)
    chance_pf_3pt = chance_pf_2pt * chance_3pa / chance_2pa
    
    chance_pf_during_2pt = chance_pf_2pt / chance_2pa
    chance_pf_during_3pt = three_point_foul_scaling_factor * chance_pf_3pt / chance_3pa 
    
    if shot_type == "two":
        probability = chance_pf_during_2pt
    else:
        probability = chance_pf_during_3pt
        
    shooting_foul_probability_dict = {
        (0, probability): True,
        (probability, 1): False
    }
    
    random_num = random.uniform(0,1)

    for prob_range in shooting_foul_probability_dict:
        if random_num > prob_range[0] and random_num < prob_range[1]:
            return shooting_foul_probability_dict[prob_range]
            # True or False

def field_goal_2(offense, defense, offense_home_court, hot, cold, foul, rush, defense_fouls):
    '''Takes in the offense, defense, if the offense is at home, if its a foul, if the offense is rushing, and returns whether or not the two goes in'''
        
    if offense_home_court:
        probability = 1/200 * (team_stats[offense]["H2P%"] + team_stats[defense]["OA2P%"])
    else:
        probability = 1/200 * (team_stats[offense]["A2P%"] + team_stats[defense]["OH2P%"])
        
    if rush:
        probability *= rush_multiplier_2pt
    if foul:
        probability *= foul_multiplier_2pt
    
    two_pointer_probability_dict = {
        (0, probability): 2,
        (probability, 1): 0
    }

    score = 0
    
    random_num = random.uniform(0,1)

    for prob_range in two_pointer_probability_dict:
        if random_num > prob_range[0] and random_num < prob_range[1]:
            score += two_pointer_probability_dict[prob_range] 
    
    if score == 0:
        
        result = "{}: Miss 2 Point Field Goal".format(offense)
        condition = "miss"
        
        if foul:
            added_score, additional_result, condition = free_throw(2, offense, offense_home_court, hot, cold)
            score += added_score
            result = result + ", Fouled on shot ({}: {} foul{}): ".format(defense, defense_fouls + 1, plural_fouls(defense_fouls + 1)) + additional_result
        else:
            two_pt_dict[offense][1] += 1

    else:
        
        result = "{}: Make 2 Point Field Goal".format(offense)
        condition = "make"
        
        if foul:
            added_score, additional_result, condition = free_throw(1, offense, offense_home_court, hot, cold)
            score += added_score
            result = result + ", Fouled on shot ({}: {} foul{}): ".format(defense, defense_fouls + 1, plural_fouls(defense_fouls + 1)) + additional_result
        
        two_pt_dict[offense][0] += 1
        two_pt_dict[offense][1] += 1
        
    return score, result, condition
    
def field_goal_3(offense, defense, offense_home_court, hot, cold, foul, rush, defense_fouls):
    '''Takes in the offense, defense, if the offense is at home, if its a foul, if the offense is rushing, and returns whether or not the three goes in'''

    if offense_home_court:
        probability = 1/200 * (team_stats[offense]["H3P%"] + team_stats[defense]["OA3P%"])
    else:
        probability = 1/200 * (team_stats[offense]["A3P%"] + team_stats[defense]["OH3P%"])
        
    if rush:
        probability *= rush_multiplier_3pt
    if foul:
        probability *= foul_multiplier_3pt
    
    three_pointer_probability_dict = {
        (0, probability): 3,
        (probability, 1): 0
    }

    score = 0
    
    random_num = random.uniform(0,1)

    for prob_range in three_pointer_probability_dict:
        if random_num > prob_range[0] and random_num < prob_range[1]:
            score += three_pointer_probability_dict[prob_range]            
            
    if score == 0:
        
        result = "{}: Miss 3 Point Field Goal".format(offense)
        condition = "miss"
        
        if foul:
            added_score, additional_result, condition = free_throw(3, offense, offense_home_court, hot, cold)
            score += added_score
            result = result + ", Fouled on shot ({}: {} foul{}): ".format(defense, defense_fouls + 1, plural_fouls(defense_fouls + 1)) + additional_result
        else:
            three_pt_dict[offense][1] += 1
        
    else:
        
        result = "{}: Make 3 Point Field Goal".format(offense)
        condition = "make"
        
        if foul:
            added_score, additional_result, condition = free_throw(1, offense, offense_home_court, hot, cold)
            score += added_score
            result = result + ", Fouled on shot ({}: {} foul{}): ".format(defense, defense_fouls + 1, plural_fouls(defense_fouls + 1)) + additional_result
    
        three_pt_dict[offense][0] += 1
        three_pt_dict[offense][1] += 1
    
    return score, result, condition
    
def free_throw(number, offense, offense_home_court, hot, cold):
    '''Takes in the number of free throws, the offensive team, and if they are at home, and returns FT result'''
    
    if offense_home_court:
        probability = team_stats[offense]["HFT%"]/100
    else:
        probability = team_stats[offense]["AFT%"]/100
    
    free_throw_probability_dict = {
        (0, probability): 1,
        (probability, 1): 0
    }
        
    total = 0
    result = 0
    for i in range(number):
        random_num = random.uniform(0,1)

        for prob_range in free_throw_probability_dict:
            if random_num > prob_range[0] and random_num < prob_range[1]:
                total += free_throw_probability_dict[prob_range]
                
                if i == number - 1:
                    if free_throw_probability_dict[prob_range] == 1:
                        condition = "make"
                    else:
                        condition = "miss"
                        
    result = "{}/{} Free throws".format(total, number)
    
    free_throw_dict[offense][0] += total
    free_throw_dict[offense][1] += number
    
    return total, result, condition
    # {0,...,number}
    
def shot_time(q, time, shot_clock, offense, defense, condition, rush_shot, last_shot):
    '''Function takes in initial conditions, and returns how long the team takes to shoot'''
    
    # get time to shoot or foul
    
    # rush variable represents how much the shot was rushed (standard stat)
    rush = 0
    
    # average out the time to take the shot under certain conditions
    if condition == "DREB" or condition == "jumpball":
        mean_score_time = 1/2 * (team_stats[offense]["TIMEaReb"] + team_stats[defense]["OTIMEaReb"])
    elif condition == "make" or condition == "def_inbound":
        mean_score_time = 1/2 * (team_stats[offense]["TIMEaMake"] + team_stats[defense]["OTIMEaMake"])
    else: # condition == "TOV" or condition == "OREB" or condition == "off_inbound"
        mean_score_time = 1/2 * (team_stats[offense]["TIMEaTOV"] + team_stats[defense]["OTIMEaTOV"])
        
    # if the team has to rush a shot, then their accuracy will decrease by an 
    # amount proportional to the difference between mean_score_time and the actual time
    
    # get the time the team has to jack up a shot
    time_to_shoot = min(shot_clock, q_end_dict[q] - time)
    
    if time_to_shoot < 0.3:
        return "time_expired", time_to_shoot, rush
    
    if rush_shot:
        if time_to_shoot < 5:
            rush = mean_score_time - time_to_shoot / 2
            mean_score_time = time_to_shoot / 2
        else:
            rush = mean_score_time - 5 # on average, a rushed shot takes 5 seconds (approximately)
            mean_score_time = 5
    elif mean_score_time > (time_to_shoot - 2) and (time_to_shoot >= 4):
        rush = mean_score_time - (time_to_shoot - 2) # make the mean score time 2 seconds before expiry
        mean_score_time = time_to_shoot - 2
    elif mean_score_time > (time_to_shoot - 2):
        rush = mean_score_time - (time_to_shoot - 2)
        mean_score_time = (time_to_shoot / 2)
    elif last_shot:
        if mean_score_time > (time_to_shoot - 2):
            rush = mean_score_time - (time_to_shoot - 2) 
        mean_score_time = time_to_shoot - 2 # make the team shoot at the very end
    
    actual_time = norm.rvs(mean_score_time, (time_to_shoot - mean_score_time)*shot_time_std_dev, 1)[0]
    
    if actual_time > time_to_shoot:
        outcome = "shot_clock_violation"
        time_taken = time_to_shoot
    else:
        outcome = "legal shot"
        time_taken = actual_time + 1 # the plus 1 accounts for the ball being in the air during the shot
    
    # minimum shot time is 1.5 seconds (of course allowing time past the buzzer)
    if time_taken < 1:
        time_taken = 1.5
            
    return outcome, time_taken, rush
    
def floor_foul_TOV_time(q, time, shot_clock, defense_rush):
    '''Function takes in initial conditions, and returns how long the opposing team has taken to foul or steal the ball'''
    
    # get the amount of time to get fouled on the floor, or turn the ball over
    
    time_to_shoot = min(shot_clock, q_end_dict[q] - time)
    
    if defense_rush:
        mean_stop_time = 2
        stop_time_dev = 1
    else:
        mean_stop_time = time_to_shoot * mean_pf_floor_TOV_multiplier
        stop_time_dev = (time_to_shoot - mean_stop_time) / 1.75
        
    actual_time = norm.rvs(mean_stop_time, stop_time_dev, 1)[0]
    
    if actual_time > time_to_shoot:
        outcome = "shot_clock_violation"
        time_taken = time_to_shoot
    else:
        outcome = "stop"
        time_taken = actual_time # no plus 1 due to the whistle
        
    if time_taken < minimum_time_to_foul_or_TOV:
        time_taken = minimum_time_to_foul_or_TOV
    
    return outcome, time_taken
    
def possession(q, time, offense, defense, offense_hot, offense_cold, 
               condition, offense_score, defense_score, defense_fouls, 
               offense_home_court, current_shot_clock
    ):
    
    ###########################################################################
    
    shot_clock = 24
    if condition == "off_inbound" or condition == "OREB":
        shot_clock = max(14, current_shot_clock)
    
    ###########################################################################
    
    # rush_shot says the team wants to shoot fast
    rush_shot = False
    # hold_ball means the team wants to hold the ball out
    hold_ball = False
    # last_shot means the team wants to shoot at the last possible second
    last_shot = False
    # need_three means the team will shoot a three
    need_three = False
    # cold means the team is on a cold streak
    cold = offense_cold
    # hot means the team is on a hot streak
    hot = offense_hot
    # bonus is just the bonus
    bonus = (defense_fouls >= bonus_amount[q])
    # pf_floor for if there was a foul on the floor
    pf_floor = False
    # defense_rush for if the other team is rushing the foul
    defense_rush = False
    # turnover if there is a turnover
    turnover = False
    # def_foul if there was a defensive foul
    def_foul = False
    
    ###########################################################################
    
    # play normally, except for holding    
    if (q in all_q[:3]) or ((q in all_q[3:]) and (q_end_dict[q] - time > 60)):
        
        # hold the ball till the end of the quarter
        if (q_end_dict[q] - time < shot_clock):
            last_shot = True 
    
    ###########################################################################
    
    # end of game scenario
    else: # boolean: (q in all_q[3:]) and (q_end_dict[q] - time <= 60)
        
        ###########################################################################
        
        # rush to jack up three
        if -9 <= score_gap(offense_score, defense_score) <= -6:
            rush_shot = True
            need_three = True

        ###########################################################################
        
        # rush to get a good shot
        # need a three only if almost no time left, otherwise get a good shot (rush)
        elif -5 <= score_gap(offense_score, defense_score) <= -3:
            
            # need a three fast
            if q_end_dict[q] - time < 30:
                rush_shot = True
                need_three = True
                
            # need a good shot
            else:
                rush_shot = True
        
        ###########################################################################
        
        # need a good shot
        elif -2 <= score_gap(offense_score, defense_score) <= 3:
            
            # want to hold ball for final shot
            if q_end_dict[q] - time < shot_clock:
                
                if score_gap(offense_score, defense_score) >= 1:
                    defense_rush = True
                
                else:
                    last_shot = True
      
        ###########################################################################
        
        # play normally, dribble out if possible
        else: 
            
            # dribble out
            if q_end_dict[q] - time < shot_clock:
                hold_ball = True

        ###########################################################################
        
    ###########################################################################
    
    # find out whether or not the possession is a turnover
    pf_floor, turnover = floor_foul_TOV(offense, defense, defense_rush)
    
    def_foul = pf_floor
    
    if pf_floor:
        # get the time taken
        outcome, time_taken = floor_foul_TOV_time(q, time, shot_clock, defense_rush)
        
        if outcome == "shot_clock_violation":
            points, result, new_condition = 0, "{}: Turnover, shot clock violation".format(offense), "def_inbound"
            
        else:
            if bonus:
                # head to the free throw line, get points and result
                result = "{}: Defensive Foul on the Floor ({}: {} foul{})".format(offense, defense, defense_fouls + 1, plural_fouls(defense_fouls + 1))
                points, additional_result, new_condition = free_throw(2, offense, offense_home_court, hot, cold)
                result += ", {} in Bonus: ".format(offense) + additional_result

            else:            
                # update points and result
                points, result, new_condition = 0, "{}: Defensive Foul on the Floor ({}: {} foul{})".format(offense, defense, defense_fouls + 1, plural_fouls(defense_fouls + 1)), "off_inbound" 
          
    elif turnover:
        # get the time taken
        outcome, time_taken = floor_foul_TOV_time(q, time, shot_clock, defense_rush)
        
        if outcome == "shot_clock_violation":
            points, result, new_condition = 0, "{}: Turnover, shot clock violation".format(offense), "def_inbound"
        
        # update points and result
        points, result, new_condition = 0, "{}: Turnover".format(offense), "TOV"
        
    else:
        # we are going to have a shot
        
        # get the time taken
        outcome, time_taken, rush = shot_time(q, time, shot_clock, offense, defense, condition, rush_shot, last_shot)
        
        if outcome == "shot_clock_violation":
            points, result, new_condition = 0, "{}: Turnover, shot clock violation".format(offense), "def_inbound"
        
        else:
            # what type of shot was it
            shot_type = type_of_shot(offense, defense, need_three)

            # was there a foul on the shot
            foul = shooting_foul(offense, defense, rush, shot_type)
            def_foul = foul

            if shot_type == "two":
                # get points and result
                points, result, new_condition = field_goal_2(offense, defense, offense_home_court, hot, cold, foul, rush, defense_fouls)
            else:
                # get points and result
                points, result, new_condition = field_goal_3(offense, defense, offense_home_court, hot, cold, foul, rush, defense_fouls)
    
        
    new_time = round(time + time_taken, 1)
    
    if new_time > q_end_dict[q]:
        new_time = q_end_dict[q]
    
    new_offense_score = offense_score + points
    new_defense_score = defense_score
    current_shot_clock = max(round(shot_clock - time_taken, 1), 0)
    
    return result, new_condition, new_time, new_offense_score, new_defense_score, current_shot_clock, def_foul
    
def rebound(offense, defense):
    
    oreb_percent = team_stats[offense]["OREB%"]
    dreb_percent = team_stats[defense]["DREB%"]
    
    offense_percent = oreb_percent / (oreb_percent + dreb_percent)
    defense_percent = dreb_percent / (oreb_percent + dreb_percent)
        
    rebound_probability_dict = {
        (0, offense_percent): "OREB",
        (offense_percent, 1): "DREB"
    }

    random_num = random.uniform(0,1)

    for prob_range in rebound_probability_dict:
        if random_num > prob_range[0] and random_num < prob_range[1]:
            return rebound_probability_dict[prob_range]
            # OREB or DREB

##########################################################################################################################
#                                                     Game Simulator                                                     #
##########################################################################################################################

def convert_initial_condition_to_dict(team1, team2, initial_condition):
    
    q = initial_condition.split(" ")[0]
    time_new = initial_condition.split(" ")[1].split(":")
    scores = initial_condition.split(" ")[2].split("-")
    fouls = initial_condition.split(" ")[4].split("-")
    team1_jumpball = initial_condition.split(" ")[6] == team1
    team1_possession = initial_condition.split(" ")[8] == team1
    shot_clock = initial_condition.split(" ")[10]
    condition = initial_condition.split(" ")[12]    
    
    return {
        "q": q,
        "time": q_end_dict[q] - (int(time_new[0]) * 60 + int(time_new[1])),
        "score": {team1: int(scores[0]), team2: int(scores[1])},
        "jumpball": {team1: team1_jumpball, team2: not team1_jumpball},
        "possession": {team1: team1_possession, team2: not team1_possession},
        "fouls": {team1: int(fouls[0]), team2: int(fouls[1])},
        "shot_clock": int(shot_clock),
        "condition": condition
    }
    
def generate_game_complex(
    game_path, year, team1, team2, team1_home, initial_condition="None", q_length=12*60, ot_length=5*60
):
  
    if initial_condition == "None":
        q_list = ["q1"]
        result_list = ["Game Started"]
        time = [0]
        score_dict = {team1: [0], team2: [0]}
        home_court_dict = {team1: team1_home, team2: not team1_home}
    else:
        initial_condition = convert_initial_condition_to_dict(team1, team2, initial_condition)
        q_list = [initial_condition["q"]]
        result_list = ["Initial Condition"]
        time = [initial_condition["time"]]
        score_dict = {team1: [initial_condition["score"][team1]], team2: [initial_condition["score"][team2]]}
        home_court_dict = {team1: team1_home, team2: not team1_home}
        
    initialize(team1, team2, q_length, ot_length, year)
    
    q_start_index = all_q.index(q_list[0])
    
    # get through game periods
    for q in all_q[q_start_index:]:
        # no need to head to next period if the score is tied (and we are in overtime periods)
        if (score_dict[team1][-1] != score_dict[team2][-1]) and q in all_q[4:] and result_list[-1] != "Initial Condition":
            break
        
        # award ball to jump ball winner at start of first quarter and overtimes
        if (q in all_q[:1] + all_q[4:]) and (result_list[-1] != "Initial Condition"):
            # jumpball if we start the game or overtime
            offense, defense = jump_ball(team1, team2)
            jumpball_winner, jumpball_loser = offense, defense
            condition = "jumpball"
        
        # award the ball to correct team at the start of quarters
        elif (q in all_q[1:4]) and (result_list[-1] != "Initial Condition"):
            if q == "q4":
                offense, defense = jumpball_winner, jumpball_loser
            else:
                offense, defense = jumpball_loser, jumpball_winner
        
        # if we are being "spawned" into a game, we want to set the parameters
        if result_list[-1] == "Initial Condition":
            
            # update possession
            if initial_condition["possession"][team1]:
                offense, defense = team1, team2
            else:
                offense, defense = team2, team1

            # update jumpball winner
            if initial_condition["jumpball"][team1]:
                jumpball_winner, jumpball_loser = team1, team2
            else:
                jumpball_winner, jumpball_loser = team2, team1
                
            # defense fouls
            defense_foul_dict = {
                team1: initial_condition["fouls"][team1],
                team2: initial_condition["fouls"][team2]
            }
            
            # current shot clock  
            current_shot_clock = initial_condition["shot_clock"]
             
            # create condition
            condition = initial_condition["condition"]
        
        else:
            
            # no need to update jumpball winner, posession
            
            defense_foul_dict = {team1: 0, team2: 0}
            current_shot_clock = 24
        
        while(True):

            # find out whether or not the offense is hot or cold
            offense_hot = False
            offense_cold = False
            
            # get the new scores, times, and description of the last play
            result, condition, new_time, new_offense_score, new_defense_score, current_shot_clock, def_foul = possession(
                q=q, time=time[-1], offense=offense, defense=defense, offense_hot=offense_hot, offense_cold=offense_cold, 
                condition=condition, offense_score=score_dict[offense][-1], defense_score=score_dict[defense][-1], 
                defense_fouls=defense_foul_dict[defense], offense_home_court=home_court_dict[offense], 
                current_shot_clock = current_shot_clock
            )

            # keep track of defensive fouls
            if def_foul:
                defense_foul_dict[defense] += 1
                    
            # keep track of turnovers
            if condition == "TOV":
                tov_dict[offense] += 1
            
            if new_time == q_end_dict[q]:

                q_list.append(q)
                time.append(new_time)
                score_dict[offense].append(new_offense_score)
                score_dict[defense].append(new_defense_score)
                result_list.append(result)
                break

            else:
                q_list.append(q)
                time.append(new_time)
                score_dict[offense].append(new_offense_score)
                score_dict[defense].append(new_defense_score)
                result_list.append(result)
                
                # rebound a missed shot
                if condition == "miss":
                    # find who gets the rebound
                    condition = rebound(offense, defense)
                    
                    # keep track of offensive rebounds
                    if condition == "DREB":
                        reb_dict[defense]["def"] += 1

                    # keep track of defensive rebounds
                    if condition == "OREB":
                        reb_dict[offense]["off"] += 1
                    
                
                # switch possession
                if condition in ["DREB", "make", "def_inbound", "TOV"]:
                    offense, defense = defense, offense
    
    ##################################################################
    
    if os.path.exists(game_path):
        for file in os.listdir(game_path):
            os.remove("{}/{}".format(game_path, file))
        os.rmdir(game_path)
    
    os.mkdir(game_path)
    
    if team1_home:
        home_team = team1
    else:
        home_team = team2
    
    with open("{}/{}".format(game_path, "game_log.txt"), 'w') as file:
        file.write("q {}:00 ot {}:00\n".format(q_length // 60, ot_length // 60))
        file.write("{} {} - Home Team: {}\n".format(team1, team2, home_team))

        for i in range(0, len(time)):
            file.write("{} {} {}-{} \t-------\t {}\n".format(q_list[i], format_time(q_list[i], q_length, ot_length, time[i]), score_dict[team1][i], score_dict[team2][i], result_list[i]).expandtabs(6))
            
    with open("{}/{}".format(game_path, "stats.txt"), 'w') as file:
        for team in [team1, team2]:
            
            file.write(team + " Stats \n\n")
            
            file.write("PTS: {}\n".format(score_dict[team][-1]))
            file.write("REB: {}\n".format(reb_dict[team]["off"] + reb_dict[team]["def"]))
            
            file.write("DREB: {}\n".format(reb_dict[team]["def"]))
            file.write("OREB: {}\n".format(reb_dict[team]["off"]))
            file.write("TOV: {}\n".format(tov_dict[team]))
            
            if three_pt_dict[team][1] + two_pt_dict[team][1] == 0:
                field_goal_percent = 0
            else:
                field_goal_percent = round((three_pt_dict[team][0] + two_pt_dict[team][0]) / (three_pt_dict[team][1] + two_pt_dict[team][1]) * 100, 1)
            file.write("FG: {}/{}, {}%\n".format(three_pt_dict[team][0] + two_pt_dict[team][0], three_pt_dict[team][1] + two_pt_dict[team][1], field_goal_percent, 1))
            
            if two_pt_dict[team][1] == 0:
                two_pt_percent = 0
            else:
                two_pt_percent = round(two_pt_dict[team][0] / two_pt_dict[team][1] * 100, 1)
            file.write("2P: {}/{}, {}%\n".format(two_pt_dict[team][0], two_pt_dict[team][1], two_pt_percent, 1))
            
            if three_pt_dict[team][1] == 0:
                three_pt_percent = 0
            else:
                three_pt_percent = round(three_pt_dict[team][0] / three_pt_dict[team][1] * 100, 1)
            file.write("3P: {}/{}, {}%\n".format(three_pt_dict[team][0], three_pt_dict[team][1], three_pt_percent, 1))
            
            if free_throw_dict[team][1] == 0:
                free_throw_percent = 0
            else:
                free_throw_percent = round(free_throw_dict[team][0] / free_throw_dict[team][1] * 100, 1)
            file.write("FT: {}/{}, {}%\n".format(free_throw_dict[team][0], free_throw_dict[team][1], free_throw_percent, 1))
            
            if team != team2:
                file.write("\n")