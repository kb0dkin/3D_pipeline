#! /bin/env python

# Populates the sql db with all of the mice, calib videos, and session recordings 
# plus chops up the videos into subviews based on the views.

import os, re, glob
import sqlite3
import argparse
import pandas as pd
from multiview_calibration_preparation import multiview_calibration_preparation

def project_populate(project_dir:str):
    '''
    Populates all of the necessary folders and SQL tables
    for the project.
    
    Also gets the bounding boxes for each of the views for 
    each day.
    
    Run this each time you add more videos or mice to the project.
    '''
    # all of our files we're expecting
    sqlite_file = os.path.join(project_dir, 'project_tracking.sqlite3')
    video_dir = os.path.join(project_dir, 'videos')
    calib_dir = os.path.join(project_dir, 'calibration_videos')
    csv_file = os.path.join(project_dir, 'mouse_list.csv')



    # make sure we have a .sqlite3 file, and videos and calibration_videos directories in the project_dir
    if not os.path.exists(sqlite_file):
        print(f'project_tracking.sqlite3 does not exist in {project_dir}')
        print(f'Please make sure you are in the right directory or run project_setup.py to create a new project directory')
        return -1
    elif not os.path.exists(video_dir):
        print(f'videos directory does not exist in {project_dir}')
        print(f'Please make sure you are in the right directory or run project_setup.py to create a new project directory')
        return -1
    elif not os.path.exists(calib_dir):
        print(f'calibration_videos directory does not exist in {project_dir}')
        print(f'Please make sure you are in the right directory or run project_setup.py to create a new project directory')
        return -1
    elif not os.path.exists(calib_dir):
        print(f'Mouse CSV file does not exist in {project_dir}')
        print(f'Please make sure you are in the right directory or run project_setup.py to create a new project directory')
        return -1


    # populate the mouse table with data from the csv
    ret = populate_mice(sql_file=sqlite_file, csv_file=csv_file)
    if ret == -1:
        return -1


    # populate the calibration videos table, plus get all of the bounding boxes
    ret = populate_calib(calib_dir=calib_dir, sql_fn=sqlite_file)
    if ret == -1:
        return -1


    ret = populate_videos(videos_dir=video_dir, sql_file = sqlite_file)
    if ret == -1:
        return -1


def populate_mice(sql_file:str, csv_file:str):
    '''
    Populates the mouse table in the SQL database
    '''

    for fn in [sql_file, csv_file]:
        if not os.path.exists(fn):
            print(f'{fn} does not exist')
            return -1
        
    # connect to the db
    con = sqlite3.connect(sql_file)

    # pull in the csv
    mouse_df = pd.read_csv(csv_file)
    full_len = len(mouse_df) # how many mice are in the CSV?

    # remove any mice  that are already in the database
    exist_df = pd.read_sql('SELECT id FROM MOUSE;', con=con)
    mouse_df = mouse_df.loc[~mouse_df['id'].isin(exist_df['id'])]
    insert_len = len(mouse_df) # how many aren't already in the sql?

    # populate the sql file
    mouse_df.to_sql('mouse', con=con, if_exists='append', index=False,
                    dtype={'id': 'text PRIMARY KEY',
                           'mouse_type': 'TEXT',
                           'sex': 'text',
                           'injection_date': 'text'})

    # how many did we insert?
    print(f'{full_len-insert_len} entries from CSV already in Mouse table;'
          'inserted {insert_len} new entries')
    con.close()
    return 0


def populate_videos(videos_dir:str, sql_file:str):
    vid_counter = 0 # keep track of the number of videos added to the 
    # for root,dir,files in os.walk(videos_dir):

    # connect to the db
    con = sqlite3.connect(sql_file)
    cur = con.cursor()

    # get a list of the mouse IDs
    sql_query = '''SELECT id FROM mouse;'''
    cur.execute(sql_query)
    mouse_list = cur.fetchall()

    for root,dir,files in os.walk(videos_dir):
        vid_files = [file for file in files if os.path.splitext(file)[-1] in ['.mp4','.avi','.tiff']]
        
        if not vid_files:
            continue
        
        for vid_file in vid_files:
            full_path = os.path.join(root, vid_file)

            # find a valid mouse ID in the file path
            mouse_id = [id[0] for id in mouse_list if id[0] in full_path]
            if len(mouse_id) > 1:
                print(f'Cannot parse mouse ID for {vid_file}')
                continue
            else:
                mouse_id = mouse_id[0]

            match = re.search('(202[3-5]\d{4})', vid_file)
            if match:
                vid_date = match.group(0)

            
            

        print(vid_files)

    con.close()




def populate_calib(calib_dir:str, sql_fn:str):
    '''
    populate the video calibration stuff. Going to just call another script
    
    '''
    calib_vids = glob.glob(os.path.join(calib_dir, '*.mp4')) # list of all mp4 calibration videos
    calib_vids += glob.glob(os.path.join(calib_dir, '*.avi')) # list of all avi calibration videos
    multiview_calibration_preparation(input_vids = calib_vids, sql_path = sql_fn) # put them into the sql db


if __name__ == "__main__":
    description = '''
                Populates all of the necessary folders and SQL tables
                for the project.

                Also gets the bounding boxes for each of the views for 
                each day.

                Run this each time you add more videos or mice to the project.
                '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('project_dir',help='project directory', default='.')
    args = parser.parse_args()

    project_populate(project_dir=args.project_dir)
