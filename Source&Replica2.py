# Necessary modules are imported
import os
import shutil
import argparse
import time
import logging
import hashlib

# This function calculates the md5 checksum of a given file
def calculate_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):  # read in 4096 byte chunks
            hash_md5.update(chunk)  # update the md5 hash with the current chunk
    return hash_md5.hexdigest()  # return the hexadecimal digest of the md5 hash

# This function syncs two folders
def sync_folders(source_folder, replica_folder, logger):
    for foldername, subfolders, filenames in os.walk(source_folder):
        for filename in filenames:
            source_file = os.path.join(foldername, filename)  # complete source file path
            # equivalent file path in replica folder
            replica_file = os.path.join(foldername.replace(source_folder, replica_folder), filename)

            # if the equivalent path does not exist in replica folder, create it
            if not os.path.exists(os.path.dirname(replica_file)):
                os.makedirs(os.path.dirname(replica_file))

            # if file does not exist in replica or differs from source, copy it from source
            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)  # copy2 also copies metadata
                logger.info(f'Copied file {source_file} to {replica_file}')  # log the copy operation

        # for files present in replica but not in source, remove them
        for filename in os.listdir(replica_folder):
            replica_file = os.path.join(replica_folder, filename)
            source_file = os.path.join(replica_folder.replace(replica_folder, source_folder), filename)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logger.info(f'Removed file {replica_file}')  # log the remove operation

# main function performing synchronization and logging
def main(source_folder, replica_folder, sync_interval, logfile):
    # set up logging to a file
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logger = logging.getLogger()
    # keep synchronizing at the given interval
    while True:
        sync_folders(source_folder, replica_folder, logger)  # call the synchronization function
        print("Sync operation complete")
        time.sleep(sync_interval)  # wait for the next sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    # arguments for source and replica folders, sync interval and logfile
    parser.add_argument('source_folder', help='Source folder path')
    parser.add_argument('replica_folder', help='Replica folder path')
    parser.add_argument('sync_interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('logfile', help='Log file path')
    args = parser.parse_args()  # parse the command line arguments
    
    # call main with the provided command line arguments
    main(args.source_folder, args.replica_folder, args.sync_interval, args.logfile)
