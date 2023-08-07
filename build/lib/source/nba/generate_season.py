from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib
import os
import sys
import json
from tabulate import tabulate
from . import INSTALL_PATH
from .generate_game import generate_game_complex
import ctypes

##########################################################################################################################
#                                                 Season Simulator Wrapper                                               #
##########################################################################################################################

def full_season_simulator():

    config_path = INSTALL_PATH + "/config_files/nba"

    with open("{}/game.json".format(config_path), "r") as file:
        game_settings = json.load(file)
    year = game_settings["year"]

    regular_season_simulator(year, game_settings, initial_condition="None")
    simulate_playoffs(year, game_settings) 
   
##########################################################################################################################
#                                                  Data Initialization                                                   #
##########################################################################################################################

def get_season_stats(year):
    
    global team_season_stats
    
    # assign team stats (wins, losses, points for, points against, home record, away record)
    team_season_stats = {}
    
    # develop a full dictionary of each teams stats over the season, including head to head vs each team
    with open("{}/data_files/team_stats/{}_team_stats.txt".format(INSTALL_PATH, year), "r") as file:
        file.readline()
        teams = file.readlines()
        for line1 in teams:
            team = line1.strip().split(" ")[0]
            team_season_stats[team] = {
                "name": team,
                "games": 0,
                "record": [0, 0],
                "home_record": [0, 0],
                "away_record": [0, 0],
                "points_for": 0,
                "points_against": 0,
                "head-to-head": {},
                "game-log": []
            }
            for line2 in teams:
                opposing_team = line2.strip().split(" ")[0]
                if opposing_team == team:
                    continue
                team_season_stats[team]["head-to-head"][opposing_team] = [0, 0]

##########################################################################################################################
#                                                     Season Simulator                                                   #
########################################################################################################################## 

def format_date(date):
    game_date = date.replace("/", "-")
    if len(game_date.split("-")[0]) == 1:
        game_date = "0" + game_date
    if len(game_date.split("-")[1]) == 1:
        game_date = game_date[:3] + "0" + game_date[3:]
    return game_date

def put_in_bracket(bracket_position, team, num_wins):
    draw.text(text_position_dict[bracket_position][0], team[1]["name"], font=normal_font, fill=black)
    draw.text(text_position_dict[bracket_position][1], "{}".format(team[0]), font=normal_font, fill=black)
    
    if bracket_position != "champion":
        center = text_position_dict[bracket_position][2]
        radius = 15

        draw.ellipse([(center[0] - radius+5, center[1] - radius+10), (center[0] + radius+5, center[1] + radius+10)],outline=black, fill=white)    
        draw.text(text_position_dict[bracket_position][2], "{}".format(num_wins), font=big_font, fill=black)

def load_list_into_playoffs(standings_list, conference, round_number, play_in=False):
        
    if play_in:
        play_in_placeholder = "PI_"
    else:
        play_in_placeholder = ""
        
    for team in standings_list:
        if team != None:
            if round_number == 5:
                bracket_position = "champion"
            else:
                bracket_position = "{}_{}{}round{}".format(conference, bracket_numbers_dict[play_in][round_number][team[0]], play_in_placeholder, round_number)
            
            num_wins = team[2]
            
            put_in_bracket(bracket_position, team, num_wins)
            
def load_bracket_into_playoffs():
    
        # Specify the font style and size
    global normal_font, big_font
    normal_font = ImageFont.truetype("times.ttf", size=15)
    big_font = ImageFont.truetype("times.ttf", size=20)

    # RGB color
    global black, white
    black = (0, 0, 0) 
    white = (255,255,255)
    
    # positions of all text positions in the figure
    global text_position_dict
    text_position_dict = {
        "west_1_round1": [(140, 82), (115, 82), (230, 78)],
        "west_8_round1": [(140, 158), (115, 158), (230, 154)],
        "west_4_round1": [(140, 233), (115, 233), (230, 229)],
        "west_5_round1": [(140, 308), (115, 308), (230, 304)],
        "west_3_round1": [(140, 395), (115, 395), (230, 391)],
        "west_6_round1": [(140, 471), (115, 471), (230, 467)],
        "west_2_round1": [(140, 547), (115, 547), (230, 543)],
        "west_7_round1": [(140, 622), (115, 622), (230, 618)],

        "east_1_round1": [(1030, 82), (1073, 82), (951, 78)],
        "east_8_round1": [(1030, 158), (1073, 158), (951, 154)],
        "east_4_round1": [(1030, 233), (1073, 233), (951, 229)],
        "east_5_round1": [(1030, 308), (1073, 308), (951, 304)],
        "east_3_round1": [(1030, 395), (1073, 395), (951, 391)],
        "east_6_round1": [(1030, 471), (1073, 471), (951, 467)],
        "east_2_round1": [(1030, 547), (1073, 547), (951, 543)],
        "east_7_round1": [(1030, 622), (1073, 622), (951, 618)],

        "west_1_8_round2": [(140+142, 124), (115+142, 124), (230+142, 120)],
        "west_4_5_round2": [(140+142, 274), (115+142, 274), (230+142, 270)],
        "west_3_6_round2": [(140+142, 436), (115+142, 436), (230+142, 432)],
        "west_2_7_round2": [(140+142, 586), (115+142, 586), (230+142, 582)],

        "east_1_8_round2": [(1030-142, 124), (1073-142, 124), (951-142, 120)],
        "east_4_5_round2": [(1030-142, 274), (1073-142, 274), (951-142, 270)],
        "east_3_6_round2": [(1030-142, 436), (1073-142, 436), (951-142, 432)],
        "east_2_7_round2": [(1030-142, 586), (1073-142, 586), (951-142, 582)],

        "west_1_8_4_5_round3": [(140+142+140, 200), (115+142+140, 200), (230+142+140, 196)],
        "west_3_6_2_7_round3": [(140+142+140, 512), (115+142+140, 512), (230+142+140, 508)],

        "east_1_8_4_5_round3": [(1030-142-140, 200), (1073-142-140, 200), (951-142-140, 196)],
        "east_3_6_2_7_round3": [(1030-142-140, 512), (1073-142-140, 512), (951-142-140, 508)],

        "west_round4": [(140+142+140, 336), (115+142+140, 336), (230+142+140, 332)],

        "east_round4": [(1030-142-140, 336), (1073-142-140, 336), (951-142-140, 332)],

        "champion": [(595, 336), (570, 336)],


        "west_7_PI_round1": [(365, 652), (345, 652), (438, 648)],
        "west_8_PI_round1": [(365, 717), (345, 717), (438, 713)],
        "west_9_PI_round1": [(365, 781), (345, 781), (438, 777)],
        "west_10_PI_round1": [(365, 846), (345, 846), (438, 842)],

        "east_7_PI_round1": [(795, 652), (835, 652), (738, 648)],
        "east_8_PI_round1": [(795, 717), (835, 717), (738, 713)],
        "east_9_PI_round1": [(795, 781), (835, 781), (738, 777)],
        "east_10_PI_round1": [(795, 846), (830, 846), (738, 842)],

        "west_7_8_PI_round2": [(478, 688), (458, 688), (551, 684)],
        "west_9_10_PI_round2": [(478, 818), (458, 818), (551, 814)],

        "east_7_8_PI_round2": [(680, 688), (720, 688), (630, 684)],
        "east_9_10_PI_round2": [(680, 818), (720, 818), (630, 814)],
    }
    
    global bracket_numbers_dict
    bracket_numbers_dict = {
        False: {
            1: {
                1: "1_",
                2: "2_",
                3: "3_",
                4: "4_",
                5: "5_",
                6: "6_",
                7: "7_",
                8: "8_",
            },
            2: {
                1: "1_8_",
                2: "2_7_",
                3: "3_6_",
                4: "4_5_",
                5: "4_5_",
                6: "3_6_",
                7: "2_7_",
                8: "1_8_",
            },
            3: {
                1: "1_8_4_5_",
                2: "3_6_2_7_",
                3: "3_6_2_7_",
                4: "1_8_4_5_",
                5: "1_8_4_5_",
                6: "3_6_2_7_",
                7: "3_6_2_7_",
                8: "1_8_4_5_",
            },
            4: {
                1: "",
                2: "",
                3: "",
                4: "",
                5: "",
                6: "",
                7: "",
                8: "",
            },
        },
        True: {
            1: {
                7: "7_",
                8: "8_",
                9: "9_",
                10: "10_",
            },
            2: {
                7: "7_8_",
                8: "7_8_",
                9: "9_10_",
                10: "9_10_",
            }
        }
    }
    
    # load east side
    for i in range(len(east_playoffs)):
        if i in [0, 1]:
            play_in = True
            round_number = i + 1
        else:
            play_in = False
            round_number = i - 1
        load_list_into_playoffs(east_playoffs[i], "east", round_number=round_number, play_in=play_in)
    
    # load west side
    for i in range(len(west_playoffs)):
        if i in [0, 1]:
            play_in = True
            round_number = i + 1
        else:
            play_in = False
            round_number = i - 1
        load_list_into_playoffs(west_playoffs[i], "west", round_number=round_number, play_in=play_in)
        
    # load champion
    load_list_into_playoffs(champion, "east", round_number=5, play_in=False)

def on_click(event):
    print("Closing Game Display...")
    plt.close()

def display_playoffs(year, playoffs_alone=False):
    
    # Open an image file
    image = Image.open("{}/data_files/NBA-Playoff-Bracket.jpg".format(INSTALL_PATH))

    # Create an ImageDraw object
    global draw
    draw = ImageDraw.Draw(image)
        
    load_bracket_into_playoffs()
    
    # Save the modified image
    if playoffs_alone:
        image.save("{}/results/nba/nba_playoffs/nba_{}_playoffs/nba_{}_playoffs.jpg".format(INSTALL_PATH, year, year))
    else:
        image.save("{}/results/nba/nba_seasons/nba_{}_season/playoffs/nba_{}_playoffs.jpg".format(INSTALL_PATH, year, year))

    # set matplotlib backend
    matplotlib.use("Qt5Agg")

    x_pos = 1000
    y_pos = 150
    width_inch = 15
    height_inch = 10
    dpi = 100

    # initialize empty plot
    print("\nOpening Playoff Display...")
    fig, ax1 = plt.subplots(1, 1, sharex=True, figsize=(width_inch,height_inch), dpi=dpi)
    plt.get_current_fig_manager().canvas.manager.window.move(x_pos, y_pos)

    # give dialogue to close the display
    print("To close the Playoff Display Box, simply click on it.")
    # Connect the on_click function to the figure canvas
    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.imshow(image)
    
    # Remove x-axis ticks
    plt.xticks([])
    # Remove y-axis ticks
    plt.yticks([])

    plt.show()
    
def simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games, round_number, conference, path, play_in=False):
    
    if number_of_games == 7:
        if team1_seed > team2_seed and round_number != 4:
            team1_home_list = [False, False, True, True, False, True, False]
        else:
            team1_home_list = [True, True, False, False, True, False, True]
            
        max_wins = 4
    else:
        if team1_seed > team2_seed:
            team1_home_list = [False]
        else:
            team1_home_list = [True]
            
        max_wins = 1
    team1_wins = 0
    team2_wins = 0
    game_log = []
    
    game_number = 1
    while (team1_wins < max_wins) and (team2_wins < max_wins):
        
        # get game file name
        if team1_home_list[game_number - 1] == True:
            game_name = "Game #{}, {} @ {}".format(game_number, team2, team1)
        else:
            game_name = "Game #{}, {} @ {}".format(game_number, team1, team2)
            
        # get the round and the conference
        if play_in:
            round_number_dict = {
                1: "Play-in 1st Round",
                2: "Play-in 2nd Round"
            }
        else:
            round_number_dict = {
                1: "1st Round",
                2: "Conference Semi-Finals",
                3: "Conference Finals",
                4: "Finals"
            }
        if round_number != 4:
            playoff_round = conference.capitalize() + " " + round_number_dict[round_number]
        else:
            playoff_round = round_number_dict[round_number]

        
        playoff_series = str(team1_seed) + " " + team1 + " vs " + str(team2_seed) + " " + team2
        
        # make playoff round directory if need be
        if playoff_round not in os.listdir(path):
            os.mkdir("{}/{}".format(path, playoff_round))
            
        if playoff_series not in os.listdir("{}/{}".format(path, playoff_round)):
            os.mkdir("{}/{}/{}".format(path, playoff_round, playoff_series))
        
        "{}/{}/{}/{}".format(path, playoff_round, playoff_series, game_name)
        
        # generate game        
        generate_game_complex(
            game_path = "{}/{}/{}/{}".format(path, playoff_round, playoff_series, game_name),
            year = game_settings["year"],
            team1 = team1, 
            team2 = team2, 
            team1_home = team1_home_list[game_number - 1], 
            initial_condition = "None", 
            q_length = 60 * game_settings["q_minutes"], 
            ot_length = 60 * game_settings["ot_minutes"]
        )

        # get game stats for the playoff bracket
        with open("{}/{}/{}/{}/{}".format(path, playoff_round, playoff_series, game_name, "stats.txt"), 'r') as game_file:
            game_points_dict = {
                team1: 0,
                team2: 0,
            }


            for line in game_file.readlines():

                if len(line) > 2:

                    if line.split(" ")[1] == "Stats":
                        current_team = line.split(" ")[0]

                    elif line.split(" ")[0][:-1] == "PTS":
                        game_points_dict[current_team] = int(line.split(" ")[1])
        
            if game_points_dict[team1] > game_points_dict[team2]:
                team1_wins += 1
                game_log.append((team1, team2, game_points_dict[team1], game_points_dict[team2]))
            else:
                team2_wins += 1
                game_log.append((team2, team1, game_points_dict[team2], game_points_dict[team1]))
        
        game_number += 1
    
    
    return team1_wins, team2_wins, game_log

def simulate_playoffs(year, game_settings, playoffs_alone=False):
    
    global east_playoffs, west_playoffs, east_playin, west_playin, champion
    
    east_playin_first_round = [None] * 4
    west_playin_first_round = [None] * 4
    
    east_playin_second_round = [None] * 2
    west_playin_second_round = [None] * 2
    
    east_playoffs_first_round = [None] * 8
    west_playoffs_first_round = [None] * 8
    
    east_playoffs_second_round = [None] * 4
    west_playoffs_second_round = [None] * 4
    
    east_playoffs_third_round = [None] * 2
    west_playoffs_third_round = [None] * 2
    
    east_playoffs_final_round = [None] * 1
    west_playoffs_final_round = [None] * 1
    
    champion = [None]
    
    east_playoffs = [
        east_playin_first_round, 
        east_playin_second_round,
        east_playoffs_first_round,
        east_playoffs_second_round,
        east_playoffs_third_round,
        east_playoffs_final_round
    ]
    
    west_playoffs = [
        west_playin_first_round, 
        west_playin_second_round,
        west_playoffs_first_round,
        west_playoffs_second_round,
        west_playoffs_third_round,
        west_playoffs_final_round
    ]
        
    east_playoffs_first_round[0] = [1, eastern_conference_standings[0], 0]
    east_playoffs_first_round[2] = [4, eastern_conference_standings[3], 0]
    east_playoffs_first_round[3] = [5, eastern_conference_standings[4], 0]
    east_playoffs_first_round[4] = [3, eastern_conference_standings[2], 0]
    east_playoffs_first_round[5] = [6, eastern_conference_standings[5], 0]
    east_playoffs_first_round[6] = [2, eastern_conference_standings[1], 0]
    
    west_playoffs_first_round[0] = [1, western_conference_standings[0], 0]
    west_playoffs_first_round[2] = [4, western_conference_standings[3], 0]
    west_playoffs_first_round[3] = [5, western_conference_standings[4], 0]
    west_playoffs_first_round[4] = [3, western_conference_standings[2], 0]
    west_playoffs_first_round[5] = [6, western_conference_standings[5], 0]
    west_playoffs_first_round[6] = [2, western_conference_standings[1], 0]
    
    for i in range(6, 10):
        
        east_playin_first_round[i-6] = [i+1, eastern_conference_standings[i], 0]
        west_playin_first_round[i-6] = [i+1, western_conference_standings[i], 0]
    
    # we want to reach into the nba schedule in files, and simulate all of the games, as well as keeping track of stats
    
    if playoffs_alone:
    
        # get fresh new directory
        if os.path.exists("{}/results/nba/nba_playoffs/nba_{}_playoffs".format(INSTALL_PATH, year)):
            for playoff_round in os.listdir("{}/results/nba/nba_playoffs/nba_{}_playoffs".format(INSTALL_PATH, year)):
                if playoff_round == "nba_{}_playoffs.jpg".format(year):
                    os.remove("{}/results/nba/nba_playoffs/nba_{}_playoffs/{}".format(INSTALL_PATH, year, playoff_round))
                    continue
                for game in os.listdir("{}/results/nba/nba_playoffs/nba_{}_playoffs/{}".format(INSTALL_PATH, year, playoff_round)):
                    for game_item in os.listdir("{}/results/nba/nba_playoffs/nba_{}_playoffs/{}/{}".format(INSTALL_PATH, year, playoff_round, game)):
                        os.remove("{}/results/nba/nba_playoffs/nba_{}_playoffs/{}/{}/{}".format(INSTALL_PATH, year, playoff_round, game, game_item))
                    os.rmdir("{}/results/nba/nba_playoffs/nba_{}_playoffs/{}/{}".format(INSTALL_PATH, year, playoff_round, game))
                os.rmdir("{}/results/nba/nba_playoffs/nba_{}_playoffs/{}".format(INSTALL_PATH, year, playoff_round))
            os.rmdir("{}/results/nba/nba_playoffs/nba_{}_playoffs".format(INSTALL_PATH, year))
        
        os.mkdir("{}/results/nba/nba_playoffs/nba_{}_playoffs".format(INSTALL_PATH, year))
        path = "{}/results/nba/nba_playoffs/nba_{}_playoffs".format(INSTALL_PATH, year)
    
    else:
        
        # get fresh new directory
        if os.path.exists("{}/results/nba/nba_seasons/nba_{}_season/playoffs".format(INSTALL_PATH, year)):
            for playoff_round in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs".format(INSTALL_PATH, year)):
                if playoff_round == "nba_{}_playoffs.jpg".format(year):
                    os.remove("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}".format(INSTALL_PATH, year, playoff_round))
                    continue
                for series in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}".format(INSTALL_PATH, year, playoff_round)):
                    for game in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}/{}".format(INSTALL_PATH, year, playoff_round, series)):
                        for game_item in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}/{}/{}".format(INSTALL_PATH, year, playoff_round, series, game)):
                            os.remove("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}/{}/{}/{}".format(INSTALL_PATH, year, playoff_round, series, game, game_item))
                        os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}/{}/{}".format(INSTALL_PATH, year, playoff_round, series, game))
                    os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}/{}".format(INSTALL_PATH, year, playoff_round, series))
                os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs/{}".format(INSTALL_PATH, year, playoff_round))
            os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs".format(INSTALL_PATH, year))
            
        os.mkdir("{}/results/nba/nba_seasons/nba_{}_season/playoffs".format(INSTALL_PATH, year))
        path = "{}/results/nba/nba_seasons/nba_{}_season/playoffs".format(INSTALL_PATH, year)
    
    ################
    #   Play in    #
    ################
    
    # simulate east play-in first round
    for i in range(0, 3, 2):
        team1 = east_playin_first_round[i][1]["name"]
        team2 = east_playin_first_round[i+1][1]["name"]
        team1_seed = east_playin_first_round[i][0]
        team2_seed = east_playin_first_round[i+1][0]
        
        team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=1, round_number=1, conference="east", path=path, play_in=True)
        
        # move the winning team onto the next round
        if (i == 0):
            if (team1_wins > team2_wins):
                # update new round
                east_playoffs_first_round[7] = [7, east_playin_first_round[i][1], 0]
                east_playin_second_round[i//2] = [team2_seed, east_playin_first_round[i+1][1], 0]
                
            else:
                # update new round
                east_playoffs_first_round[7] = [7, east_playin_first_round[i+1][1], 0]
                east_playin_second_round[i//2] = [team1_seed, east_playin_first_round[i][1], 0]
                
        else:
            if (team1_wins > team2_wins):
                # update new round
                east_playin_second_round[i//2] = [team1_seed, east_playin_first_round[i][1], 0]
            
            else:
                # update new round
                east_playin_second_round[i//2] = [team2_seed, east_playin_first_round[i+1][1], 0]
                
        # update this round
        east_playin_first_round[i][2] = team1_wins
        east_playin_first_round[i+1][2] = team2_wins
    
    # simulate east play-in second round    
    for i in range(1):
        team1 = east_playin_second_round[i][1]["name"]
        team2 = east_playin_second_round[i+1][1]["name"]
        team1_seed = east_playin_second_round[i][0]
        team2_seed = east_playin_second_round[i+1][0]
        
        team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=1, round_number=2, conference="east", path=path, play_in=True)
        
        # move the winning team onto the next round
        if (team1_wins > team2_wins):
            # update new round
            east_playoffs_first_round[1] = [8, east_playin_second_round[i][1], 0]
            
        else:
            # update new round
            east_playoffs_first_round[1] = [8, east_playin_second_round[i+1][1], 0]
            
        # update this round
        east_playin_second_round[i][2] = team1_wins
        east_playin_second_round[i+1][2] = team2_wins
        
    # simulate west play-in
    for i in range(0, 3, 2):
        team1 = west_playin_first_round[i][1]["name"]
        team2 = west_playin_first_round[i+1][1]["name"]
        team1_seed = west_playin_first_round[i][0]
        team2_seed = west_playin_first_round[i+1][0]
        
        team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=1, round_number=1, conference="west", path=path, play_in=True)
    
        # move the winning team onto the next round
        if (i == 0):
            if (team1_wins > team2_wins):
                # update new round
                west_playoffs_first_round[7] = [7, west_playin_first_round[i][1], 0]
                west_playin_second_round[i//2] = [team2_seed, west_playin_first_round[i+1][1], 0]
                
            else:
                # update new round
                west_playoffs_first_round[7] = [7, west_playin_first_round[i+1][1], 0]
                west_playin_second_round[i//2] = [team1_seed, west_playin_first_round[i][1], 0]
                
        else:
            if (team1_wins > team2_wins):
                # update new round
                west_playin_second_round[i//2] = [team1_seed, west_playin_first_round[i][1], 0]
            
            else:
                # update new round
                west_playin_second_round[i//2] = [team2_seed, west_playin_first_round[i+1][1], 0]
                
        # update this round
        west_playin_first_round[i][2] = team1_wins
        west_playin_first_round[i+1][2] = team2_wins
    
    for i in range(1):
        team1 = west_playin_second_round[i][1]["name"]
        team2 = west_playin_second_round[i+1][1]["name"]
        team1_seed = west_playin_second_round[i][0]
        team2_seed = west_playin_second_round[i+1][0]
        
        team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=1, round_number=2, conference="west", path=path, play_in=True)
        
        # move the winning team onto the next round
        if (team1_wins > team2_wins):
            # update new round
            west_playoffs_first_round[1] = [8, west_playin_second_round[i][1], 0]
            
        else:
            # update new round
            west_playoffs_first_round[1] = [8, west_playin_second_round[i+1][1], 0]
            
        # update this round
        west_playin_second_round[i][2] = team1_wins
        west_playin_second_round[i+1][2] = team2_wins
        
    ################
    #   Playoffs   #
    ################
    
    playoff_round_length = [8, 4, 2]
        
    # simulate the east playoffs    
    for j in range(2, 5):
        for i in range(0, playoff_round_length[j-2], 2):
        
            team1 = east_playoffs[j][i][1]["name"]
            team2 = east_playoffs[j][i+1][1]["name"]
            team1_seed = east_playoffs[j][i][0]
            team2_seed = east_playoffs[j][i+1][0]

            team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=7, round_number=j-1, conference="east", path=path, play_in=False)

            # move the winning team onto the next round
            if (team1_wins > team2_wins):
                # update new round
                east_playoffs[j+1][i//2] = [team1_seed, east_playoffs[j][i][1], 0]

            else:
                # update new round
                east_playoffs[j+1][i//2] = [team2_seed, east_playoffs[j][i+1][1], 0]

            # update this round
            east_playoffs[j][i][2] = team1_wins
            east_playoffs[j][i+1][2] = team2_wins
        
    # simulate the west playoffs
    for j in range(2, 5):
        for i in range(0, playoff_round_length[j-2], 2):
            team1 = west_playoffs[j][i][1]["name"]
            team2 = west_playoffs[j][i+1][1]["name"]
            team1_seed = west_playoffs[j][i][0]
            team2_seed = west_playoffs[j][i+1][0]

            team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=7, round_number=j-1, conference="west", path=path, play_in=False)

            # move the winning team onto the next round
            if (team1_wins > team2_wins):
                # update new round
                west_playoffs[j+1][i//2] = [team1_seed, west_playoffs[j][i][1], 0]

            else:
                # update new round
                west_playoffs[j+1][i//2] = [team2_seed, west_playoffs[j][i+1][1], 0]

            # update this round
            west_playoffs[j][i][2] = team1_wins
            west_playoffs[j][i+1][2] = team2_wins
            
            
    # simulate the finals
    team1 = west_playoffs[5][0][1]["name"]
    team2 = east_playoffs[5][0][1]["name"]
    team1_seed = west_playoffs[5][0][0]
    team2_seed = east_playoffs[5][0][0]
    
    team1_wins, team2_wins, game_log = simulate_series(game_settings, team1_seed, team2_seed, team1, team2, number_of_games=7, round_number=4, conference="east", path=path, play_in=False)
    
    if (team1_wins > team2_wins):
        # update new round
        champion = [[team1_seed, west_playoffs[5][0][1], 0]]

    else:
        # update new round
        champion = [[team2_seed, east_playoffs[5][0][1], 0]]

    # update this round
    west_playoffs[5][0][2] = team1_wins
    east_playoffs[5][0][2] = team2_wins
        
    display_playoffs(year, playoffs_alone)

def calc_games_back(best_record, record):
    return str(1/2 * ((best_record[0] - record[0]) + (record[1] - best_record[1])))

def calc_percentage(record):
    if (record[0] + record[1]) > 0:
        return (round(record[0] / (record[0] + record[1]), 3))
    else:
        return 0

def get_last_10(game_log):
    length = min(10, len(game_log))
    
    if length == 0:
        return "0-0"
    else:
        wins = 0
        losses = 0
        for i in range(-length, 0):
            if game_log[i] == "W":
                wins += 1
            else:
                losses += 1
        return "{}-{}".format(wins, losses)

def get_streak(game_log):

    if len(game_log) > 0:
        current = game_log[-1]
        i = -1
        while (-i <= len(game_log)) and game_log[i] == current:
            i -= 1
        return "{}{}".format(current, -(i+1))
    else:
        return "-"

def print_standings():
    
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    east_table = [["Team", "Record", "Pct", "GB", "Home", "Away", "L10", "Streak"]]
    east_best_record = None
    east_rank = 1
    
    for team in eastern_conference_standings:
        if east_best_record == None:
            east_best_record = team["record"]
        east_table.append([
            east_rank,
            team["name"], 
            "{}-{}".format(team["record"][0], team["record"][1]),
            calc_percentage(team["record"]),
            calc_games_back(east_best_record, team["record"]),
            "{}-{}".format(team["home_record"][0], team["home_record"][1]),
            "{}-{}".format(team["away_record"][0], team["away_record"][1]),
            get_last_10(team["game-log"]),
            get_streak(team["game-log"])  
        ])
        east_rank += 1
    
    west_table = [["Team", "Record", "Pct", "GB", "Home", "Away", "L10", "Streak"]]
    west_best_record = None
    west_rank = 1
    
    for team in western_conference_standings:
        if west_best_record == None:
            west_best_record = team["record"]
        west_table.append([
            west_rank,
            team["name"], 
            "{}-{}".format(team["record"][0], team["record"][1]),
            calc_percentage(team["record"]),
            calc_games_back(west_best_record, team["record"]),
            "{}-{}".format(team["home_record"][0], team["home_record"][1]),
            "{}-{}".format(team["away_record"][0], team["away_record"][1]),
            get_last_10(team["game-log"]),
            get_streak(team["game-log"])
        ])
        west_rank += 1
        
    east_table = tabulate(east_table, headers='firstrow', tablefmt='fancy_grid', floatfmt=(".3f", ".3f", ".3f", ".3f", ".1f"))
    west_table = tabulate(west_table, headers='firstrow', tablefmt='fancy_grid', floatfmt=(".3f", ".3f", ".3f", ".3f", ".1f"))
    
    # print("\033[1m\n\nEastern Conference\033[0m\n{}\n\033[1m\n\nWestern Conference\033[0m{}\n".format(east_table, west_table).count("\n"))
    sys.stdout.write("\033[1m\n\nEastern Conference\033[0m\n{}\n\033[1m\n\nWestern Conference\033[0m\n{}\n".format(east_table, west_table))

    
def produce_standings():
    
    global east_conference, west_conference, atlantic_division, central_division, southeast_division, northwest_division, pacific_division, southwest_division
    
    # conferences
    east_conference = ["ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DET", "IND", "MIA", "MIL", "NYK", "ORL", "PHI", "TOR", "WAS"]
    west_conference = ["DAL", "DEN", "GSW", "HOU", "LAC", "LAL", "MEM", "MIN", "NOP", "OKC", "PHO", "POR", "SAC", "SAS", "UTA"]
    
    # east divisions
    atlantic_division = ["BOS", "BKN", "NYK", "PHI", "TOR"]
    central_division = ["CHI", "CLE", "DET", "IND", "MIL"]
    southeast_division = ["ATL", "CHA", "MIA", "ORL", "WAS"]
    
    # west divisions
    northwest_division = ["DEN", "MIN", "OKC", "POR", "UTA"]
    pacific_division = ["GSW", "LAC", "LAL", "PHO", "SAC"]
    southwest_division = ["DAL", "HOU", "MEM", "NOP", "SAS"]
    
    ordered_list = []
    
    for team in team_season_stats:
        if len(ordered_list) == 0:
            ordered_list.append(team_season_stats[team])
        else:
            i = 0
            while i < len(ordered_list) and (ordered_list[i]["record"][0] + ordered_list[i]["record"][1]) > 0 and (team_season_stats[team]["record"][0] + team_season_stats[team]["record"][1]) > 0 and ordered_list[i]["record"][0] / (ordered_list[i]["record"][0] + ordered_list[i]["record"][1]) > team_season_stats[team]["record"][0] / (team_season_stats[team]["record"][0] + team_season_stats[team]["record"][1]):
                i += 1
            ordered_list.insert(i, team_season_stats[team])
    
    global eastern_conference_standings, western_conference_standings, atlantic_division_standings, central_division_standings, southeast_division_standings, northwest_division_standings, pacific_division_standings, southwest_division_standings
    
    eastern_conference_standings = []
    western_conference_standings = []
    
    atlantic_division_standings = []
    central_division_standings = []
    southeast_division_standings = []
    northwest_division_standings = []
    pacific_division_standings = []
    southwest_division_standings = []
            
    for team in ordered_list:
        if team["name"] in east_conference:            
            eastern_conference_standings.append(team)
        else:
            western_conference_standings.append(team)
        
        for division_name, division in [(atlantic_division, atlantic_division_standings), (central_division, central_division_standings), (southeast_division, southeast_division_standings), (northwest_division, northwest_division_standings), (pacific_division, pacific_division_standings), (southwest_division, southwest_division_standings)]:
            if team["name"] in division_name:
                division.append(team)
        
    return eastern_conference_standings, western_conference_standings, atlantic_division_standings, central_division_standings, southeast_division_standings, northwest_division_standings, pacific_division_standings, southwest_division_standings

def display_standings():
    produce_standings()
    print_standings()

def regular_season_simulator(year, game_settings, initial_condition):
    
    get_season_stats(year)
    
    # we want to reach into the nba schedule in files, and simulate all of the games, as well as keeping track of stats
    
    # get fresh new directory
    if os.path.exists("{}/results/nba/nba_seasons/nba_{}_season".format(INSTALL_PATH, year)):
        for month in os.listdir("{}/results/nba/nba_seasons/nba_{}_season".format(INSTALL_PATH, year)):
            for game in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/{}".format(INSTALL_PATH, year, month)):
                if game == "nba_{}_playoffs.jpg".format(year):
                    os.remove("{}/results/nba/nba_seasons/nba_{}_season/{}/{}".format(INSTALL_PATH, year, month, game))
                    continue
                for game_item in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/{}/{}".format(INSTALL_PATH, year, month, game)):
                    if month != "playoffs":
                        os.remove("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}".format(INSTALL_PATH, year, month, game, game_item))
                    else:
                        for next_item in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}".format(INSTALL_PATH, year, month, game, game_item)):
                            for next_item2 in os.listdir("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}/{}".format(INSTALL_PATH, year, month, game, game_item, next_item)):
                                os.remove("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}/{}/{}".format(INSTALL_PATH, year, month, game, game_item, next_item, next_item2))
                            os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}/{}".format(INSTALL_PATH, year, month, game, game_item, next_item))
                        os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}".format(INSTALL_PATH, year, month, game, game_item))
                os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/{}/{}".format(INSTALL_PATH, year, month, game))
            os.rmdir("{}/results/nba/nba_seasons/nba_{}_season/{}".format(INSTALL_PATH, year, month))
        os.rmdir("{}/results/nba/nba_seasons/nba_{}_season".format(INSTALL_PATH, year))
        
    os.mkdir("{}/results/nba/nba_seasons/nba_{}_season".format(INSTALL_PATH, year))
    month_list = []
    
    with open("{}/data_files/nba_schedules/{}_schedule.txt".format(INSTALL_PATH, year), "r") as file:
        file.readline()
        first = True # have first variable to know when it has only been one iteration
        for line in file.readlines():
            line_list = line.split(" ")
            
            game_date = format_date(line_list[2])
            game_month = game_date.split("-")[0]
            
            if game_month not in month_list:
                os.mkdir("{}/results/nba/nba_seasons/nba_{}_season/{}".format(INSTALL_PATH, year, game_month))
                month_list.append(game_month)
            
            home_team = line_list[4]
            away_team = line_list[3]
            
            game_name = "{}, {} @ {}".format(game_date, away_team, home_team)
            generate_game_complex(
                game_path = "{}/results/nba/nba_seasons/nba_{}_season/{}/{}".format(INSTALL_PATH, year, game_month, game_name),
                year = game_settings["year"],
                team1 = home_team, 
                team2 = away_team, 
                team1_home = True, 
                initial_condition = "None", 
                q_length = 60 * game_settings["q_minutes"], 
                ot_length = 60 * game_settings["ot_minutes"]
            )

            # get game stats for the season
            with open("{}/results/nba/nba_seasons/nba_{}_season/{}/{}/{}".format(INSTALL_PATH, year, game_month, game_name, "stats.txt")) as game_file:
                game_stats_dict = {
                    home_team: {
                        "PTS_for": 0, 
                        "PTS_against": 0,
                        "opp_team": away_team
                    },
                    away_team: {
                        "PTS_for": 0, 
                        "PTS_against": 0,
                        "opp_team": home_team
                    }
                }

                current_team = ""
                opposing_team = ""

                for line in game_file.readlines():


                    if len(line) > 2:

                        if line.split(" ")[1] == "Stats":
                            current_team = line.split(" ")[0]
                            if current_team == home_team:
                                opposing_team = away_team
                            else:
                                opposing_team = home_team

                        elif line.split(" ")[0][:-1] == "PTS":
                            game_stats_dict[current_team]["PTS_for"] = int(line.split(" ")[1])
                            game_stats_dict[opposing_team]["PTS_against"] = int(line.split(" ")[1])
          
            
            # consolidate these stats in the greater season stats
            team_season_stats[home_team]["games"] += 1
            team_season_stats[away_team]["games"] += 1
            
            if game_stats_dict[home_team]["PTS_for"] > game_stats_dict[home_team]["PTS_against"]:
                # home team wins
                team_season_stats[home_team]["record"][0] += 1 # add win to winning team
                team_season_stats[away_team]["record"][1] += 1 # add loss to losing team
                
                team_season_stats[home_team]["game-log"].append("W") # add win to game log
                team_season_stats[away_team]["game-log"].append("L") # add loss to game log
                
                team_season_stats[home_team]["home_record"][0] += 1 # add home win to home team
                team_season_stats[away_team]["away_record"][1] += 1 # add away loss to away team
                
                # update head to head
                team_season_stats[home_team]["head-to-head"][away_team][0] += 1 # add head-to-head win to home team
                team_season_stats[away_team]["head-to-head"][home_team][1] += 1 # add head-to-head loss to away team
            
            else:
                # away team wins
                team_season_stats[home_team]["record"][1] += 1 # add loss to losing team
                team_season_stats[away_team]["record"][0] += 1 # add win to winning team
                
                team_season_stats[home_team]["game-log"].append("L") # add loss to game log
                team_season_stats[away_team]["game-log"].append("W") # add win to game log
                
                team_season_stats[home_team]["home_record"][1] += 1 # add home loss to home team
                team_season_stats[away_team]["away_record"][0] += 1 # add away win to away team
                
                # update head to head
                team_season_stats[home_team]["head-to-head"][away_team][1] += 1 # add head-to-head loss to home team
                team_season_stats[away_team]["head-to-head"][home_team][0] += 1 # add head-to-head win to away team
                
            # update points for and against
            team_season_stats[home_team]["points_for"] += game_stats_dict[home_team]["PTS_for"]
            team_season_stats[home_team]["points_against"] += game_stats_dict[home_team]["PTS_against"]
            
            team_season_stats[away_team]["points_for"] += game_stats_dict[away_team]["PTS_for"]
            team_season_stats[away_team]["points_against"] += game_stats_dict[away_team]["PTS_against"]
            
            
            if not first:
                clear_output(72)
            first = False
            sys.stdout.write("\rSimulating the {} NBA season... Currently in the regular season, at: {}".format(year, game_date))
            display_standings()
            sys.stdout.flush()

def clear_output(num_lines):
    sys.stdout.write("\033[F" * num_lines)
    sys.stdout.write("\033[K" * num_lines)
    sys.stdout.flush()