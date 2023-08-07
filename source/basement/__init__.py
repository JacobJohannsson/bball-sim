import os

# Get the user's home directory (C:/Users/user/ on Windows)
home_directory = os.path.expanduser("~")

# Specify the directory name to create in the user's home directory
directory_name = "bball"

INSTALL_PATH = os.path.join(home_directory, directory_name)