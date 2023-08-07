import json
from . import INSTALL_PATH

##########################################################################################################################
#                                                     Edit JSON Files                                                    #
##########################################################################################################################

def edit_game(q_minutes, ot_minutes, pace, three_penalty, tight_game, randomness):
    
    config_path = INSTALL_PATH + "/config_files/basement"

    arg_dictionary = {
        "q_minutes": q_minutes,
        "ot_minutes": ot_minutes,
        "pace": pace,
        "three_penalty": three_penalty,
        "tight_game": tight_game,
        "randomness": randomness
    }

    print("Opening game.json config file...")

    with open("{}/game.json".format(config_path), "r") as file:
        game_settings = json.load(file)

    for arg in arg_dictionary:
        if arg_dictionary[arg] != None:
            game_settings[arg] = arg_dictionary[arg]

    # serializing json
    json_object = json.dumps(game_settings, indent=4)

    print("Writing to game.json config file...")
    
    # writing to config file
    with open("{}/game.json".format(config_path), "w") as file:
        file.write(json_object)

def edit_team1(name, skill, threefreq):

    config_path = INSTALL_PATH + "/config_files/basement"

    arg_dictionary = {
        "name": name,
        "skill": skill,
        "threefreq": threefreq
    }

    print("Opening game.json config file...")

    with open("{}/team1.json".format(config_path), "r") as file:
        team1_settings = json.load(file)

    for arg in arg_dictionary:
        if arg_dictionary[arg] != None:
            team1_settings[arg] = arg_dictionary[arg]

    # serializing json
    json_object = json.dumps(team1_settings, indent=4)

    print("Writing to team1.json config file...")

    # writing to config file
    with open("{}/team1.json".format(config_path), "w") as file:
        file.write(json_object)

    

def edit_team2(name, skill, threefreq):

    config_path = INSTALL_PATH + "/config_files/basement"

    arg_dictionary = {
        "name": name,
        "skill": skill,
        "threefreq": threefreq
    }

    print("Opening game.json config file...")

    with open("{}/team2.json".format(config_path), "r") as file:
        team2_settings = json.load(file)

    for arg in arg_dictionary:
        if arg_dictionary[arg] != None:
            team2_settings[arg] = arg_dictionary[arg]

    # serializing json
    json_object = json.dumps(team2_settings, indent=4)

    print("Writing to team2.json config file...")

    # writing to config file
    with open("{}/team2.json".format(config_path), "w") as file:
        file.write(json_object)