import os
import shutil

def install_directory():
    # Get the user's home directory (C:/Users/user/ on Windows)
    home_directory = os.path.expanduser("~")

    # Specify the directory name to create in the user's home directory
    directory_name = "bball"
    install_path = os.path.join(home_directory, directory_name)

    # Create the directory if it doesn't exist
    if not os.path.exists(install_path):
        
        # Make directory 
        # os.makedirs(install_path)

        # Copy files from the source directory to the install directory
        current_directory_path = os.path.abspath(__file__)
        package_directory = os.path.dirname(current_directory_path)

        # Copy files ffrom apckage
        source_directory = "{}/bball".format(package_directory)  # Replace with the source directory of your files
        shutil.copytree(source_directory, install_path)

        print(install_path)

        os.makedirs("{}/{}/{}/{}".format(install_path, "results", "basement_games", "generated_games"))
        os.makedirs("{}/{}/{}".format(install_path, "results", "nba"))
        os.makedirs("{}/{}/{}/{}".format(install_path, "results", "nba", "nba_games"))
        os.makedirs("{}/{}/{}/{}".format(install_path, "results", "nba", "nba_playoffs"))
        os.makedirs("{}/{}/{}/{}".format(install_path, "results", "nba", "nba_probabilities"))
        os.makedirs("{}/{}/{}/{}".format(install_path, "results", "nba", "nba_seasons"))

if __name__ == "__main__":
    install_directory()
