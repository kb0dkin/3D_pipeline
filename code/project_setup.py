#! /bin/env python


import sqlite3
import os
import argparse
import pkg_resources
import requests
import zipfile
import shutil
import gdown



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
    if not os.path.exists(calib_dir):
        os.mkdir(calib_dir)
    else:
        print(f'{calib_dir} already exists')

    # create a directory for the mouse videos
    vid_dir = os.path.join(directory,'videos')
    if not os.path.exists(vid_dir):
        os.mkdir(vid_dir)
    else:
        print(f'{vid_dir} already exists')
    

    # create the sqlite3 file with all appropriate files
    sqlite_setup(directory=directory)

    # create the mouse list csv
    csv_fname = os.path.join(directory, 'mouse_list.csv')
    with open(csv_fname, 'a+') as fid:
        headers = 'id,injection_date,injection_type,sex\n'
        fid.write(headers)

    
    # create either a SLEAP or MARS directory depending on what we created
    if 'sleap' in [p.project_name for p in pkg_resources.working_set]:
        keypoints_dir = os.path.join(directory, 'SLEAP')

        # One directory for the sideviews, one for the bottom-up
        for view_dir in ['sideview','underside']:
            subdirs = [os.path.join(keypoints_dir,view_dir, subdir) for subdir in ['models','predictions']]
            for subdir in subdirs:
                # create a subdir for models and predictions for each view
                os.makedirs(subdir, mode=0o755, exist_ok=True)

        # download underside model    
        model_url = "https://drive.google.com/file/d/1QPFnk2kZWCUHA8m94xrIVGF4G5hAbgn8/view?usp=sharing"
        # file_id = '1QPFnk2kZWCUHA8m94xrIVGF4G5hAbgn8'
        download_gdrive(model_url, os.path.join(keypoints_dir, 'underside', 'models'))
        # download_zip(model_url, os.path.join(keypoints_dir, 'underside', 'models'))
        # download sideview model
        model_url = "https://drive.google.com/file/d/1rYhYsoLhDgm99CsXDfXezRzfREiWh8mZ/view?usp=sharing"
        # download_zip(model_url, os.path.join(keypoints_dir, 'sideview', 'models'))
        # file_id = '1rYhYsoLhDgm99CsXDfXezRzfREiWh8mZ'
        download_gdrive(model_url, os.path.join(keypoints_dir, 'sideview', 'models'))



    elif 'mars' in [p.project_name for p in pkg_resources.working_set]:
        print('Kevin, get MARS setup running')
    

    # copy config.toml to the base directory
    print(f'Copying default config.toml into {directory}')
    src_toml = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.toml')
    dest_toml = os.path.join(directory,'config.toml')
    shutil.copy(src_toml , dest_toml)



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
   

# function to download and save a zip file
def download_zip(url:str, save_path:str, chunk_size=128):
    zip_fn = os.path.join(save_path,'temp.zip')

    # open a stream using http get
    r = requests.get(url, stream=True)
    # open the file and save in 128 byte chunks
    print(f'Downloading {url}')
    with open(zip_fn, 'wb') as fid:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fid.write(chunk)
    
    print(f'Extracing files from {zip_fn}')
    zipfile.ZipFile(zip_fn).extractall(save_path)
    
    print(f'Deleting original zip {zip_fn}')
    os.remove(zip_fn)


def download_gdrive(model_url:str, save_path:str, chunk_size = 32768):
    print(f'Downloading {model_url}')
    zip_fn = os.path.join(save_path, 'temp.zip')
    gdown.download(model_url, zip_fn, fuzzy=True)

    print(f'Extracting files from {save_path}')
    zipfile.ZipFile(zip_fn).extractall(save_path)

    print(f'Deleting original zip {zip_fn}')
    os.remove(zip_fn)


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
