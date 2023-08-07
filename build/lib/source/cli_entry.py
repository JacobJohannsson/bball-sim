#!/usr/bin/env python3

import click
from . import INSTALL_PATH
import os

from source.config import basement_view_game_config
from source.config import basement_view_team1_config
from source.config import basement_view_team2_config
from source.config import basement_edit_game_config
from source.config import basement_edit_team1_config
from source.config import basement_edit_team2_config

from source.config import nba_view_game_config
from source.config import nba_edit_game_config

from source.basement.generate_game import generate_game_simple
from source.basement.list_games import list_basement_games

from source.nba.generate_game import generate_single_game
from source.nba.generate_probability import game_probability
from source.nba.generate_season import full_season_simulator
from source.nba.list_games import list_nba_games

from source.display_game import display_game_log, display_final_score 
from source.display_game import plot_game, animate_game
# from ..source.plot_game import 
# from ..source.organization import 

@click.group()
def cli():
    pass

@cli.group()
def basement():
    pass

@basement.command()
@click.option("-n", "--game-name", type=str, help="Name the game that is going to be generated")
@click.option("-l", "--game-log", is_flag=True, help="Display the generated game log")
@click.option("-f", "--final-score", is_flag=True, help="Display final score of the game")
def generate_game(game_name, game_log, final_score):
    print()
    game_path = generate_game_simple(game_name)
    if game_log:
        display_game_log(game_path)
    if final_score:
        display_final_score(game_path)
    print()

@basement.command()
@click.option("-g", "--game-name", type=str, help="Path to the game starting after ../basement_games/..")
@click.option("-a", "--animate", is_flag=True, help="Animate the game display, at a desired pace")
@click.option("-s", "--speed", type=float, default=0.25, help="Time in seconds between every game update (Default: 0.25)")
@click.option("-j", "--jump-frames", type=int, default=1, help="Speed up animation by jumping multiple frames (Default: 1)")
@click.option("--colour1", type=str, default="green", help="Team 1's colour in the game plot")
@click.option("--colour2", type=str, default="skyblue", help="Team 2's colour in the game plot")
def display_game(game_name, animate, speed, jump_frames, colour1, colour2):    
    print()
    game_path = INSTALL_PATH + "/results/basement_games/" + game_name
    if not animate:
        plot_game(game_path, False, colour1, colour2)
    else:
        animate_game(game_path, False, speed, jump_frames, colour1, colour2)
    print()

@basement.command()
def list():
    print()
    list_basement_games()
    print()

@basement.group()
def config():
    pass

@config.group()
def view():
    pass

@view.command()
def game():
    print()
    basement_view_game_config()
    print()
    

@view.command()
def team1():
    print()
    basement_view_team1_config()
    print()

@view.command()
def team2():
    print()
    basement_view_team2_config()
    print()


@config.group()
def edit():
    pass

@edit.command()
@click.option("--q_minutes", type=int, default=None, help="Change the number of minutes per quarter.")
@click.option("--ot_minutes", type=int, default=None, help="Change the number of minutes per overtime.")
@click.option("--pace", type=float, default=None, help="Change the pace of the game. Number must be >= 4.")
@click.option("--three-penalty", type=float, default=None, help="Change the penalty of taking a three.")
@click.option("--tight-game", type=float, default=None, help="Change how tight the games are.")
@click.option("--randomness", type=float, default=None, help="Change how random the outcomes are.")
def game(q_minutes, ot_minutes, pace, three_penalty, tight_game, randomness):
    print()
    basement_edit_game_config(q_minutes, ot_minutes, pace, three_penalty, tight_game, randomness)
    print()

@edit.command()
@click.option("--name", type=int, default=None, help="Change the name of team1.")
@click.option("--skill", type=int, default=None, help="Change the skill points of team1 on a RAPTOR scale (1500 is average).")
@click.option("--threefreq", type=float, default=None, help="Change the three point frequency of team1.")
def team1(name, skill, threefreq):
    print()
    basement_edit_team1_config(name, skill, threefreq)
    print()

@edit.command()
@click.option("--name", type=int, default=None, help="Change the name of team2.")
@click.option("--skill", type=int, default=None, help="Change the skill points of team2 on a RAPTOR scale (1500 is average).")
@click.option("--threefreq", type=float, default=None, help="Change the three point frequency of team2.")
def team2(name, skill, threefreq):
    print()
    basement_edit_team2_config(name, skill, threefreq)
    print()

@cli.group()
def nba():
    pass

@nba.command()
@click.option("-h" , "--home-team", type=str, help="The home team participating in the game")
@click.option("-a" , "--away-team", type=str, help="The away team participating in the game")
@click.option("-i", "--initial-condition", is_flag=True, help="Use initial condition, which is accessible and modifyable in the initial_condition config file .....")
@click.option("-l", "--game-log", is_flag=True, help="Display the generated game log")
@click.option("-f", "--final-score", is_flag=True, help="Display final score of the game")
def generate_game(home_team, away_team, initial_condition, game_log, final_score):
    print()
    if not initial_condition:
        game_path = generate_single_game(home_team, away_team, initial_condition="None")
    else:
        # still need to adapt to extract initial condition from json file
        game_path = generate_single_game(home_team, away_team, initial_condition="None")

    if game_log:
        display_game_log(game_path)
    if final_score:
        display_final_score(game_path)
    print()

@nba.command()
@click.option("-h" , "--home-team", type=str, help="The home team participating in the game")
@click.option("-a" , "--away-team", type=str, help="The away team participating in the game")
@click.option("-g", "--games", type=int, default=2500, help="Number of games that should be simulated for the probability (Default: 2500).")
@click.option("-i", "--initial-condition", is_flag=True, help="Use initial condition, which is accessible and modifyable in the initial_condition config file .....")
def generate_probability(home_team, away_team, games, initial_condition):
    print()
    if not initial_condition:
        game_probability(home_team, away_team, games, initial_condition="None")
    else:
        # still need to adapt to extract initial condition from json file
        game_probability(home_team, away_team, games, initial_condition="None")
    print()

@nba.command()
@click.option("-i", "--initial-condition", is_flag=True, help="Use initial condition, which is accessible and modifyable in the initial_condition config file .....")
def generate_season(initial_condition):
    print()
    if not initial_condition:
        full_season_simulator()
    else:
        # still need to adapt to extract initial condition from json file
        full_season_simulator()
    print()

@nba.command()
@click.option("-g", "--game-name", type=str, help="Path to the game starting after ../basement_games/..")
@click.option("-a", "--animate", is_flag=True, help="Animate the game display, at a desired pace")
@click.option("-s", "--speed", type=float, default=0.25, help="Time in seconds between every game update (Default: 0.25)")
@click.option("-j", "--jump-frames", type=int, default=1, help="Speed up animation by jumping multiple frames (Default: 1)")
@click.option("--colour1", type=str, default="green", help="Team 1's colour in the game plot")
@click.option("--colour2", type=str, default="skyblue", help="Team 2's colour in the game plot")
def display_game(game_name, animate, speed, jump_frames, colour1, colour2):    
    print()
    game_path = INSTALL_PATH + "/results/nba/" + game_name
    if not animate:
        plot_game(game_path, True, colour1, colour2)
    else:
        animate_game(game_path, True, speed, jump_frames, colour1, colour2)
    print()

@nba.command()
@click.option("-g", "--nba-games", is_flag=True, help="Display games in the nba_games folder")
@click.option("-s", "--nba-seasons", is_flag=True, help="Display games in the nba_seasons folder")
@click.option("-p", "--nba-playoffs", is_flag=True, help="Display games in the nba_playoffs folder")
def list_games(nba_games, nba_seasons, nba_playoffs):
    print()
    list_nba_games(nba_games, nba_seasons, nba_playoffs)
    print()

@nba.group()
def config():
    pass

@config.group()
def view():
    pass

@view.command()
def game():
    print()
    nba_view_game_config()
    print()

@config.group()
def edit():
    pass

@edit.command()
@click.option("--q_minutes", type=int, default=None, help="Change the number of minutes per quarter.")
@click.option("--ot_minutes", type=int, default=None, help="Change the number of minutes per overtime.")
@click.option("--year", type=float, default=None, help="Change which year the data is coming from.")
def game(q_minutes, ot_minutes, year):
    print()
    basement_edit_game_config(q_minutes, ot_minutes, year)
    print()

if __name__ == "__main__":
    cli()