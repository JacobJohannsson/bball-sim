# Basketball Simulator CLI



To setup the package, navigate to this folder, and run `pip install .`, this will do the following:
1. Create a new folder `~/bball`, which stores the config files, and all results.
2. Install executable package, called `bball_games`.


## Basement Games Simulator

Run `bball_games basement ...`, the options here are:
1. `config`, from which the game presets can be viewed and modified.
2. `display-game`, which displays created games in a lead chart.
3. `generate-game`, which generates new games with the presets.
4. `list`, which lists the current set of basement games, and how to display them.

## NBA Games Simulator

Run `bball_games nba ...`, the options here are:
1. `config`, from which the game presets can be viewed and modified.
2. `display-game`, which displays created games in a lead chart.
3. `generate-game`, which generates new games with the presets
4. `generate-probability`, which generates game probabilities (even with initial game conditions, customizable through `config`).
5. `generate-season`, which simulates and entire season + playoffs, and displays the results.
6. `list-games`, which lists the current set of nba games, and how to display them.
