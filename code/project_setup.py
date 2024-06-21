#! /bin/env python


import sqlite3
import os
import argparse
import pkg_resources
import requests



# main command
def project_setup(directory):
    '''Sets up a project directory for our 3D tracking pipeline.
                    \t * creates a new project directory if it doesn't exist
                    \t * creates a calibration video directory if it doesn't exist
                    \t * sets up a sqlite3 file with all necessary tables
                    \t * creates a SLEAP or MARS subdirectory with trained models inside
                    \t * creates and AniPose .toml settings file'''

    # create the base directory if needed
    if not os.path.exists(directory):
        os.mkdir(directory)
        print(f'Created directory {directory}')
    else:
        print(f'{directory} already exists. Continuing')

    # create a directory for the calibration videos
    calib_dir = os.path.join(directory,'calibration_videos') 
    if not os.path.exists():
        os.mkdir(calib_dir)
    else:
        print(f'{calib_dir} already exists')


    # create the sqlite3 file with all appropriate files
    sqlite_setup(directory=directory)

    # create the mouse list csv
    csv_fname = os.path.join(directory, 'mouse_list.csv')
    with open(csv_fname, 'a+') as fid:
        headers = ['id,injection_date,injection_type,sex\n']
        fid.write(headers)

    
    # create either a SLEAP or MARS directory depending on what we created
    if 'sleap' in [p.project_name for p in pkg_resources.working_set]:
        keypoints_dir = os.path.join(directory, 'SLEAP')
    elif 'mars' in [p.project_name for p in pkg_resources.working_set]:
        os.mkdir()
    






def sqlite_setup(directory:str):
    # create the sqlite3 file for our 3D pipeline

    # boot us if the directory doesn't exist 
    if not os.path.exists(directory):
        print('Base Directory {directory} does not exist!')
        exit()

    # create the file and the cursor
    sqlite_file = os.path.join(directory, 'project_tracking.sqlite3')
    if os.path.exists(sqlite_file):
        print(f'{sqlite_file} already exists')
    con = sqlite3.connect(sqlite_file)
    cur = con.cursor()


    # create the mouse table
    mouse_creation = '''
                        CREATE TABLE IF NOT EXISTS mouse 
                        (id text, injection_date text, injection_type text, sex text);
                        '''
    cur.execute(mouse_creation)

    # create the recordings table
    session_creation = ''' 
                        CREATE TABLE IF NOT EXISTS session
                        (mouse_id text, time text, task text, experimenter text,
                        enclosure text, comments text,
                        FOREIGN KEY (mouse_id) REFERENCES "mouse" ([id]));
                        '''
    cur.execute(session_creation)

    # create the videos table
    videos_creation = ''' 
                        CREATE TABLE IF NOT EXISTS videos (
                            relative_path text, 
                            session_id text,
                            description text,
                            FOREIGN KEY (session_id) REFERENCES "session" ([rowid])
                        );'''
    cur.execute(videos_creation)

    # calibration table
    calibration_creation = ''' 
                        CREATE TABLE IF NOT EXISTS calibration (
                            relative_path text,
                            boundary blob,
                            intrinsic blob,
                            extrinsic blob
                        );'''
    cur.execute(calibration_creation)
   

if __name__ == '__main__':
    # command line calls
    description = '''Sets up a project directory for our 3D tracking pipeline.
                    \t * creates a new directory if it doesn't exits
                    \t * sets up a sqlite3 file with all necessary tables
                    \t * creates a SLEAP or MARS subdirectory with trained models inside
                    \t * creates and AniPose .toml settings file'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('d', help = 'Project Directory')
    args = parser.parse_args()

    project_setup(directory= args.d)
