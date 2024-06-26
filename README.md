# 3D_pipeline

This pipeline steps through 3D markerless motion tracking for our food handling tasks. It uses a combination of 2D motion tracking systems and [Anipose](github.com/lambdaloop/anipose). It also includes tools to use AWS labeling services to put together initial training sets, like in [MARS](github.com/neuroethology/MARS_developer).

## Installation and Required Tools
__NOTE:__ At the moment this only works for Windows and Linux, since we're relying on Python 3.7 which isn't available for the OSX-ARM64 chipset. We should probably see if we can use a later version of Python since 3.7 is no longer supported

* 2D markerless motion tracking can be done using either [MARS developer](github.com/neuroethology/MARS_developer) or [SLEAP](sleap.ai)
* [Anipose](github.com/lambdaloop/anipose) for camera calibration and marker triangulation

All required tools can be installed using the provided Conda file. Refer to [Anaconda's documentation](https://docs.anaconda.com/miniconda/) for installation and usage of Conda.

First you should update your conda solver to **libmamba**
```
conda update -n base conda
conda install -n base conda-libmamba-solver
conda config --set solver libmamba
```

To install the Sleap-based toolchain:
```
conda env create -n pipeline_3D -f pipeline_sleap.yml
```


To install the MARS-based toolchain:
```
conda env create -n pipeline_3D -f pipeline_MARS
```

Then activate the environment
```
conda activate pipeline_3D
```


## Project Setup
The pipeline I built around SLEAP/MARS and AniPose uses sqlite to keep track of the calibration videos and recording sessions. 

First, run the [project setup](code/project_setup.py) python script
```
python code/project_setup.py [project_directory]
```

This will 
1. create a new directory if it doesn't exist
1. setup a sqlite file with all of the necessary tables
1. create a SLEAP or MARS subdirectory and place all settings files and pretrained models inside
1. create an Anipose __.toml__ file with the settings we have found to work the best


## Populating project with new data
Next, we have to put data (mice information and videos) into the project. 

You have to do a few preparatory pieces:
1. Open the "mouse_list.csv" using a spreadsheet software like Excel or OpenOffice. Populate the spreadsheet with the mice you have.
1. Place all videos that you want to analyze in the "videos" directory. Videos need to be separated into subdirectories by mouse, and the mouse id needs to be in the directory tree.
    * eg. ```videos/mouse_id/20231105/chocolate_chips.mp4``` 
1. Place all calibration videos into the "calibration_videos" directory. The video filenames **must** contain the date in the ```_YYYYmmdd_``` including the leading and trailing underscores
    * eg. ```Basler_0101_20231105_.mp4```


---
Next, run the run the [project populate](code/project_populate.py) python script
```
python code/project_populate.py [directory]
```

This script:
1. Updates the sqlite database with any new mice that have been added to the __mouse_list.csv__ file
1. Adds any new calibration videos to the sqlite database, and has the user mark the bounding box for each view
1. Adds any new videos to the sqlite database, then
    1. Associate it with the calibration video that was recorded most recently for that day
    1. Crops the video into different views based on that calibration video



## Predict keypoints with Sleap
We'll be using our pre-built Sleap models to predict our keypoints. 

```
python code/predict_all.py [directory]
```

For each session in the sqlite DB:
1. Predicts the "North/South/East/West" videos in SLEAP using the sideview models, and the "center" video using the underside video
    - ``` sleap-track -m [centroid.slp] -m [centered-instance.slp] --tracking hungarian --max-tracks 1 --```
1. Converts the predictions into something that AniPose can understand.
    - ```Sleap2Anipose.py```
1. Triangulates the data using the configuration from that day.

