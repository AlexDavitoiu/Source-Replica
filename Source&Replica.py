import hashlib
import os
import shutil
import time
import sys
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree

class bcolors: #Simple color printing for ui components
    OKGREEN = '\033[92m'
    USER_PROMPT = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

source_directory = 'Source' #Defining the default source folder (the folder to be cloned)
replica_directory = 'Replica' #Defining the default replica folder (the folder to clone to)
log_file = 'log.txt' #Defines default log file name

max_name_len_files = 0
max_name_len_variables = 0

fail_counter = 0 
file_names = []
replica_hashes = []
failed_list = []

def check_dir(dir):

    clear_screen()
    exists = os.path.isdir(dir)

    if not exists:
        os.makedirs(dir)
        print("Folder -> " + dir + "does not exist.")
        print("Created folder -> ", dir)
        time.sleep(2)

def create_log(log):

        f = open(log,"w")
        f.close()

        print("File -> " + log + "does not exist.")
        print("Created file -> ", log)
        time.sleep(2)

def check_file(log):

    clear_screen()
    exists = os.path.isfile(log)

    if not exists:

        create_log(log)
    
    else:
        print("Log file already exists. Deleting...")

        create_log(log)

def reset_variables(): #Function to clear program variables after an execution
    file_names.clear()
    replica_hashes.clear()
    failed_list.clear()

def checksum_calculator(file):

    file_name = file
    with open(file_name, 'rb') as file_to_check:

            data = file_to_check.read()    

            md5_returned = hashlib.md5(data).hexdigest()
            
            return md5_returned

def replica_hash_calculation(): #Calculate md5 hashes for each file in replica folder
    
    for file in file_names:
    
        file_name = file

        md5_returned = checksum_calculator(file_name)
        
        replica_hashes.append(md5_returned)

def file_list_construction(directory): #Building a list with all file names + the directory prefix

    for file_name in os.listdir(directory):
        f = os.path.join(directory, file_name)

        if os.path.isfile(f):
            file_names.append(f)

def file_checksum(file): #Calculate md5 hash for a specific file

        file_name = file

        md5_returned = checksum_calculator(file_name)
            
        return md5_returned

def new_file_detection(): #Detect if a new file has been created in the source folder
    if len(replica_hashes) < len(file_names):
        directory_clone()
        #main()

def empty_failsafe(): #Detect if the replica folder is empty
    if len(replica_hashes) == 0:
            directory_clone()

def file_clone(file): #Clone specific file
            shutil.copyfile(source_directory, replica_directory, file, follow_symlinks=True)
        
def directory_clone(): #Clone whole directory

            clear_screen()

            for failed_file in failed_list:
                print("[LOG] Cloned file - " + failed_file)

                with open(log_file, "a") as file_log:
                    file_log.write("[LOG] Cloned file - " + failed_file + "\n")

            time.sleep(3)

            copy_tree(source_directory, replica_directory)

def directory_remove(): #Remove whole directory

            remove_tree(replica_directory)
            main()

def file_deleted_detection(): #Detect if a file has been deleted
    if len(replica_hashes) > len(file_names):
        directory_remove()
        directory_clone()

def auto_timer(timer_value): #Timer for automatically backing up and basic timer display
            timer_value_seconds = int(timer_value)

            if timer_value_seconds >= 60:
                timer_value_seconds = 60
            
            while timer_value_seconds >= 1:
                if timer_value_seconds > 9:
                    clear_screen()
                    print("0:" + str(timer_value_seconds))
                    
                else:
                    clear_screen()
                    print("0:0" + str(timer_value_seconds))     
                    
                time.sleep(1)
                timer_value_seconds -= 1
            
            print ("Files have been checked and cloned")
            time.sleep(1)

def clear_screen(): #Clear screen command, ui
    os.system('cls')

def main(): #Main function that combines everything

        max_name_len_files = 0

        check_dir(source_directory)
        check_dir(replica_directory)

        reset_variables()
        clear_screen()
        fail_counter = 0
        file_list_construction(replica_directory)
        replica_hash_calculation()
        file_names.clear()
        file_list_construction(source_directory)

        empty_failsafe()
        new_file_detection()
        file_deleted_detection()


        print ("|-------Source&Replica---------@P0siti0n45-------|")
        print("|Source Folder  -> " + source_directory + " " * (30 - len(source_directory)) + "|")
        print("|Replica Folder -> " + replica_directory + " " * (30 - len(replica_directory)) + "|")
        print("|Log File       -> " + log_file  + " " * (30 - len(log_file)) + "|")

        print ("|------------------------------------------------|")

        for file,hash in zip(file_names,replica_hashes):

            space_compensation = len(str(file))

            if space_compensation > max_name_len_files:
                max_name_len_files = space_compensation

        for file,hash in zip(file_names,replica_hashes):
            md5_returned = file_checksum(file)
            original_md5 = hash
            
            space_compensation = len(str(file))
            
            if original_md5 == md5_returned:

                print("|" , end = '')
                print(bcolors.OKGREEN + file + " "*(max_name_len_files - space_compensation) + " | Passed!" + bcolors.ENDC, end = '')
                print(' ' *((38 - max_name_len_files)), end = '')
                print("|")
                print ("|------------------------------------------------|")
            else:
                fail_counter += 1
                failed_list.append(file)
                print("|" , end = '')
                print(bcolors.FAIL + file +  " "*(max_name_len_files - space_compensation) + " | Failed!" + bcolors.ENDC, end = '')
                print(' ' *((38 - max_name_len_files)), end = '')
                print("|")
                print ("|------------------------------------------------|")

        if fail_counter > 0:
            print(bcolors.FAIL + "File discrepancy detected!" + bcolors.ENDC)
        
        for failed_file in failed_list:
            print("[LOG] Failed to verify -> " + failed_file)

            with open(log_file, "a") as file_log:
            
                file_log.write("[LOG] Failed to verify -> " + failed_file + "\n")

        print(bcolors.USER_PROMPT + "Input 1 to check again." + bcolors.ENDC)
        if fail_counter > 0:
            print(bcolors.USER_PROMPT + "Input 2 to mirror the Source folder to Replica folder." + bcolors.ENDC)

        print(bcolors.USER_PROMPT + "Input 3 to start a timer that automatically mirrors the source folder on a custom time interval" + bcolors.ENDC)
        print(bcolors.USER_PROMPT + "Input 4 to exit." + bcolors.ENDC)

        user_input = input()

        if user_input == "1":
            main()

        if user_input == "2":
            directory_clone()
            main()
            
        if user_input == "3":
            print(bcolors.USER_PROMPT + "Please input a value between 1-60 seconds for the automatic backup." + bcolors.ENDC)
            timer_value = input()
            while True:
                auto_timer(timer_value)
                reset_variables()
                clear_screen()
                fail_counter = 0
                file_list_construction(replica_directory)
                replica_hash_calculation()
                file_names.clear()
                file_list_construction(source_directory)

                empty_failsafe()
                new_file_detection()
                file_deleted_detection()

                directory_clone()

        if user_input == "4":
            exit()

if len(sys.argv) == 1:
    clear_screen()
    print ("----Source&Replica - @P0siti0n45 ----")
    print ("Arguments: Source&Replica.py 'source_directory' 'replica_directory 'log_file' -- To set custom source, replica and log locations")
    print ("Arguments: Source&Replica.py 'default' -- To use default program values")
    exit()

if len(sys.argv) == 2 and sys.argv[1] == 'default': #Default value choice starts the program directly
    main()

if len(sys.argv) == 4: #Custom value choice sets the variables according to user input then starts the program accordingly
    for arg in sys.argv:

        source_directory = sys.argv[1] #Defining the source folder (the folder to be cloned)
        replica_directory = sys.argv[2] #Defining the replica folder (the folder to clone to)
        log_file = sys.argv[3] #Defining the log file to use

else: #Invalid command usage handling
    clear_screen()
    print("Invalid syntax")
    print("Run the program without any arguments to see command usage")
    exit()

check_file(log_file)

main() #Start main