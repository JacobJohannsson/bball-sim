from tabulate import tabulate
import numpy as np
import csv
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from . import INSTALL_PATH

##########################################################################################################################
#                                                     Display game log                                                   #
##########################################################################################################################

def display_game_log(game_path):

    with open("{}/{}".format(game_path, "game_log.txt"), 'r') as file:
        contents = file.read()
        game_name = game_path.split("/")[-1].split(".")[0]
        print("\nContents of game file: {}".format(game_name))
        print(contents, end='')

def display_final_score(game_path):
    with open("{}/{}".format(game_path, "game_log.txt"), 'r') as file:
        contents = file.readlines()
        team1 = contents[1].split()[0]
        team2 = contents[1].split()[1]
        team1_score = contents[-1].split()[2].split("-")[0]
        team2_score = contents[-1].split()[2].split("-")[1]
        print("\n{} Final Score: {}\n{} Final Score: {}".format(team1, team1_score, team2, team2_score))

##########################################################################################################################
#                                                  Data Initialization                                                   #
##########################################################################################################################

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
    with open("{}/data_files/team_colours/{}_colours.txt".format(INSTALL_PATH, year), 'r') as file:
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
        with open("{}/config_files/nba/game.json".format(INSTALL_PATH), 'r') as file:
            game_config = json.load(file)
            q_length = 60 * game_config["q_minutes"]
            ot_length = 60 * game_config["ot_minutes"]
        get_dicts(q_length=q_length, ot_length=ot_length)

        #need to find a way to replace this year argument with something better
        get_colours("2022-23")
    else:
        with open("{}/config_files/basement/game.json".format(INSTALL_PATH), 'r') as file:
            game_config = json.load(file)
            q_length = 60 * game_config["q_minutes"]
            ot_length = 60 * game_config["ot_minutes"]
        get_dicts(q_length=q_length, ot_length=ot_length)

##########################################################################################################################
#                                                Plotting Games Snapshots                                                #
##########################################################################################################################


def plot_game_snapshot(fig, ax1, line, caption, name1, name2, time, q, score1, score2, lead, zeros, colour1="green", colour2="skyblue"):

    # obtain largest leads
    largest_lead1 = abs(max(lead))
    largest_lead2 = abs(min(lead))
    largest_lead = max(abs(max(lead)), abs(min(lead)))
    
    longest_run1 = 0
    longest_run2 = 0
    
    # get longest run for team1
    for i in range(len(time)):
        current_run = 0
        for j in range(i, len(time)):
            if score2[j] != score2[i]:
                break
            current_run = score1[j] - score1[i]
        if current_run > longest_run1:
            longest_run1 = current_run
            
    # get longest run for team2
    for i in range(len(time)):
        current_run = 0
        for j in range(i, len(time)):
            if score1[j] != score1[i]:
                break
            current_run = score2[j] - score2[i]
        if current_run > longest_run2:
            longest_run2 = current_run

    line.set_data(time, lead)

    # add y axis lines at intervals of 5
    min_y = -(5*(largest_lead // 5) + 5)
    max_y = (5*(largest_lead // 5) + 5)
    for y in range(min_y, max_y+5, 5):
        ax1.axhline(y=y, color='black', linewidth=0.25)

    # add x axis lines at intervals of every quarter
    x = "q1"
    ax1.axvline(x=q_start_dict[x], color='black', linewidth=0.25)
    for x in all_q:    
        ax1.axvline(x=q_end_dict[x], color='black', linewidth=0.25)
        if x == q:
            break

    # fill spaces where team1 has the lead
    ax1.fill_between(time, lead, zeros, where=score1 >= score2,
                     facecolor=colour1, interpolate=True)
    
    # fill spaces where team2 has the lead
    ax1.fill_between(time, lead, zeros, where=score1 <= score2,
                     facecolor=colour2, interpolate=True)
    
    # set yticks every 5 points
    ax1.set_yticks(list(range(min_y, max_y+5, 5)))
    
    # no xticks
    ax1.set_xticks([])
    
    # set title
    ax1.set_title('{} vs {}'.format(name1, name2))  
        
    # set up table formatting
    quarters = ["        "]
    i = 0
    for x in all_q:
        quarters.append("  " + x.upper())
        if x == q:
            break
    quarters.append("  TOT")
            
    quarter_scoring1 = ["{}".format(name1)]
    quarter_scoring2 = ["{}".format(name2)]
    for x in all_q:
        start_time = q_start_dict[x]
        end_time = q_end_dict[x]
        for i in range(len(time)):
            if time[i] <= start_time:
                start = i
            if time[i] <= end_time:
                end = i
        quarter_scoring1.append(score1[end] - score1[start])
        quarter_scoring2.append(score2[end] - score2[start])
        if x == q:
            break
    quarter_scoring1.append(score1[-1])
    quarter_scoring2.append(score2[-1])
     
    # get table
    table = tabulate([quarters, quarter_scoring1, quarter_scoring2], headers='firstrow', tablefmt='fancy_grid')

    # set caption with table and stats
    caption.set_text('{}\'s Largest Lead: {}           {}\'s Largest Lead: {}\n{}\'s Longest Run: {}           {}\'s Longest Run: {}\n\n{}'.format(
        name1, largest_lead1, name2, largest_lead2, name1, longest_run1, name2, longest_run2, table
    ))

###########################################################################################################################
#                                                          Close Game                                                     #
###########################################################################################################################

def on_click(event):
    print("Closing Game Display...")
    plt.close()

###########################################################################################################################
#                                                      Plot Single Game                                                   #
###########################################################################################################################

    
def plot_game(game_path, nba, colour1="green", colour2="skyblue"):

    initialize(nba)

    # read from the game log and obtain time, scores, etc.
    time = [0]
    score1 = [0]
    score2 = [0]
    q_list = ["q1"]

    with open("{}/{}".format(game_path, "game_log.txt"), 'r') as file:
        line = file.readline()
        q_length = int(line.split(" ")[1].split(":")[0]) * 60
        ot_length = int(line.split(" ")[3].split(":")[0]) * 60
        
        line = file.readline().split()
        name1 = line[0]
        name2 = line[1]

        if nba:
            #assign team colours if using nba games
            colour1, colour2 = assign_colours(name1, name2)

        lines = csv.reader(file)
        for line in lines:

            q = line[0].split(" ")[0]
            q_list.append(q)

            time_new = line[0].split(" ")[1].split(":")
            if (q[:1] == "q"):
                time_new = q_length - (int(time_new[0]) * 60 + int(time_new[1]))
            else:
                time_new = ot_length - (int(time_new[0]) * 60 + int(time_new[1]))
            time_new = q_start_dict[q] + time_new

            score1_new = int(line[0].split(" ")[2].split("-")[0])
            score2_new = int(line[0].split(" ")[2].split("-")[1])

            time.extend([time_new-0.01, time_new])
            score1.extend([score1[-1],score1_new])
            score2.extend([score2[-1],score2_new])

        time.extend([q_end_dict[q]])
        score1.extend([score1[-1]])
        score2.extend([score2[-1]])

    time = np.array(time)
    score1 = np.array(score1)
    score2 = np.array(score2)
    lead = score1 - score2
    zeros = np.zeros(len(score2))

    # set matplotlib backend
    matplotlib.use("Qt5Agg")

    x_pos = 1000
    y_pos = 150
    width_inch = 15
    height_inch = 10
    dpi = 100

    # initialize empty plot
    print("Opening Game Display...")
    fig, ax1 = plt.subplots(1, 1, sharex=True, figsize=(width_inch,height_inch), dpi=dpi)
    line, = ax1.plot([],[],lw=0)
    caption = ax1.text(
        0.5, 
        -0.175, 
        '', 
        ha='center', 
        va='center', 
        fontfamily="monospace", 
        transform=ax1.transAxes, 
        fontsize=10, 
        verticalalignment='top'
    )
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)
    caption.set_text('')
    plt.get_current_fig_manager().canvas.manager.window.move(x_pos, y_pos)

    # give dialogue about game plotting
    print("Plotting the Game...")

    # give dialogue to close the display
    print("To close the Game Display Box, simply click on it.")

    # Connect the on_click function to the figure canvas
    fig.canvas.mpl_connect('button_press_event', on_click)

    # plot the game (which is only one snapshot)
    plot_game_snapshot(fig=fig, ax1=ax1, line=line, caption=caption, name1=name1, name2=name2, time=time, q=q, score1=score1, score2=score2, lead=lead, zeros=zeros, colour1=colour1, colour2=colour2)
    plt.show()

##########################################################################################################################
#                                                  Plotting Games Slowly                                                 #
##########################################################################################################################


def update_plot(i, fig, ax1, line, caption, name1, name2, time, q_list, score1, score2, lead, zeros, colour1, colour2):
    # call plot_game_snapshot function, slicing game stats with [:i+1 to plot periodically]
    plot_game_snapshot(fig=fig, ax1=ax1, line=line, caption=caption, name1=name1, name2=name2, time=time[:i+1], q=q_list[i], score1=score1[:i+1], score2=score2[:i+1], lead=lead[:i+1], zeros=zeros[:i+1], colour1=colour1, colour2=colour2)
    
    return line,

def animate_game(game_path, nba, speed, jump_frames, colour1="green", colour2="skyblue"):

    initialize(nba)
    
    # read from the game log and obtain time, scores, etc.
    time = [0]
    score1 = [0]
    score2 = [0]
    q_list = ["q1"]

    with open("{}/{}".format(game_path, "game_log.txt"), 'r') as file:
        line = file.readline()
        q_length = int(line.split(" ")[1].split(":")[0]) * 60
        ot_length = int(line.split(" ")[3].split(":")[0]) * 60
        
        line = file.readline().split()
        name1 = line[0]
        name2 = line[1]

        if nba:
            #assign team colours if using nba games
            colour1, colour2 = assign_colours(name1, name2)

        lines = csv.reader(file)
        for line in lines:

            q = line[0].split(" ")[0]

            time_new = line[0].split(" ")[1].split(":")
            if (q[:1] == "q"):
                time_new = q_length - (int(time_new[0]) * 60 + int(time_new[1]))
            else:
                time_new = ot_length - (int(time_new[0]) * 60 + int(time_new[1]))
            time_new = q_start_dict[q] + time_new

            score1_new = int(line[0].split(" ")[2].split("-")[0])
            score2_new = int(line[0].split(" ")[2].split("-")[1])

            time.extend([time_new-0.01, time_new])
            score1.extend([score1[-1],score1_new])
            score2.extend([score2[-1],score2_new])
            q_list.extend([q, q])

        time.extend([q_end_dict[q]])
        score1.extend([score1[-1]])
        score2.extend([score2[-1]])
        q_list.extend([q])

    time = np.array(time)
    score1 = np.array(score1)
    score2 = np.array(score2)
    lead = score1 - score2
    zeros = np.zeros(len(score2))

    # set matplotlib backend
    matplotlib.use("Qt5Agg")

    x_pos = 1000
    y_pos = 150
    width_inch = 15
    height_inch = 10
    dpi = 100

    # initialize empty plot
    print("Opening Game Display...")
    fig, ax1 = plt.subplots(1, 1, sharex=True, figsize=(width_inch,height_inch), dpi=dpi)
    line, = ax1.plot([],[],lw=0)
    plt.get_current_fig_manager().canvas.manager.window.move(x_pos, y_pos)
    caption = ax1.text(
        0.5, 
        -0.175, 
        '', 
        ha='center', 
        va='center', 
        fontfamily="monospace", 
        transform=ax1.transAxes, 
        fontsize=10, 
        verticalalignment='top'
    )
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)
    caption.set_text('')
    plt.get_current_fig_manager().canvas.manager.window.move(x_pos, y_pos)

    # give dialogue about game animation
    print("Animating the Game...")

    # give dialogue to close the display
    print("To close the Game Display Box, simply click on it.")

    # Connect the on_click function to the figure canvas
    fig.canvas.mpl_connect('button_press_event', on_click)

    # get frame range used in this animation
    index_range = list(range(0, len(time)-1, jump_frames)) + [len(time)-1]
    
    # start plot animation
    ani = animation.FuncAnimation(fig, update_plot, frames=index_range, fargs=(fig, ax1, line, caption, name1, name2, time, q_list, score1, score2, lead, zeros, colour1, colour2), repeat=False, interval=speed * 1000)
    plt.show()