import os

def clean_nba_games():
    # access and clean the nba_games directory
    for game_folder in os.listdir("nba_games"):
        for file in os.listdir("nba_games/{}".format(game_folder)):
            os.remove("nba_games/{}/{}".format(game_folder, file))
        os.rmdir("nba_games/{}".format(game_folder))
        
def clean_nba_probabilities():
    # access and clean the nba_games directory
    for matchup_folder in os.listdir("nba_probabilities"):
        for file in os.listdir("nba_probabilities/{}".format(matchup_folder)):
            os.remove("nba_probabilities/{}/{}".format(matchup_folder, file))
        os.rmdir("nba_probabilities/{}".format(matchup_folder))

def backup_data_files():
    with open("nba_statistics/team_stats.txt", "r") as file:
        lines = file.readlines()
        with open("nba_statistics/backup.txt" , "w") as file:
            for line in lines:
                file.write(line)

def backup_stats():
    with open("nba_statistics/team_stats.txt", "r") as file:
        lines = file.readlines()
        with open("nba_statistics/backup.txt" , "w") as file:
            for line in lines:
                file.write(line)