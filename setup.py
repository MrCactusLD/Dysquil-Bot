import time

setup_files = []
setup_files.append("settings")
setup_files.append("spotify")


def main():

    for file in setup_files:
        with open('setup/' + file +"_def.ini", 'r') as fin:
            data = fin.read().splitlines(True)
        with open(file + ".ini",'w') as fout:
            fout.writelines(data[1:])

    print("Default files have been created succesfully:\n\tsettings.ini,\n\tspotify.ini\nListed files should now be edited.\nProgram is gonna close now")
    time.sleep(5)
    exit("Setup has finished")
    
    