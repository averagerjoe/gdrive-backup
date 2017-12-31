#! /bin/python

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import hashlib
import tarfile
import datetime
import logging
from sys import exit
from os import path, listdir, remove, stat

backup_dir = '/root/Documents/oscp/backups/'
notes_path = '/root/Documents/oscp/oscp_notes'

def init_logging():
    log_file = '/root/Documents/oscp/backup_script/logs/backup.log'
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s:  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=path.basename(source_dir))

def authenticate():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return gauth

def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def main():
    global backup_dir
    global notes_path
    
    init_logging()

    temp_name = "oscp_notes_temp.tar.gz"
    temp_file = backup_dir + temp_name
    try:
        make_tarfile(temp_file, notes_path)
    except Exception as e:
        logging.critical(e.message)
        exit(0)

    backup_files = listdir(backup_dir)
    try:
        file1 = stat(backup_dir + backup_files[0])
        file2 = stat(backup_dir + backup_files[1])
    except Exception as e:
        logging.critical(e.message)
        exit(0)
    #print file1.st_size
    #print file2.st_size

    # checking file size and an indicator of change
    # sha256 hash as an indicator did not work

    if file1.st_size == (file2.st_size + 7):
        logging.info("Previous backup is up-to-date")
        logging.info("Cleaning up...")
        remove(temp_file)
        logging.info("Exiting...")
    else:
        logging.info("Previous backup is not up-to-date")
        logging.info("Removing old backups")
        remove(backup_dir + backup_files[0])
        remove(backup_dir + backup_files[1])
        time = datetime.datetime.now()
        new_backup_path = backup_dir + "oscp_notes_" + time.strftime("%b_%d_%Y") + ".tar.gz"
        try:
            make_tarfile(new_backup_path, notes_path)
        except Exception as e:
            logging.critical(e.message)
            exit(0)

        try: 
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)
            f = drive.CreateFile()
            f.SetContentFile(new_backup_path)
            f.Upload()
        except Exception as e:
            logging.critical(e.message)
            exit(0)


if __name__ == "__main__":
    main()


