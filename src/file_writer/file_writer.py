import os
def writeToFile(content):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, "process.txt")
    
    with open(file_path, 'a') as file:
        file.write(content + "\n")