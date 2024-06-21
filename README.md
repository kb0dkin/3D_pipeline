# 3D_pipeline

This pipeline steps through 3D markerless motion tracking for our food handling tasks. It uses a combination of 2D motion tracking systems and [Anipose](github.com/lambdaloop/anipose). It also includes tools to use AWS labeling services to put together initial training sets, like in [MARS](github.com/neuroethology/MARS_developer).

## Installation and Required Tools
* 2D markerless motion tracking can be done using either [MARS developer](github.com/neuroethology/MARS_developer) or [SLEAP](sleap.ai)
* [Anipose](github.com/lambdaloop/anipose) for camera calibration and marker triangulation

All required tools can be installed using the provided Conda file. Refer to [Anaconda's documentation](https://docs.anaconda.com/miniconda/) for installation and usage of Conda.

First you should update your conda solver to **libmamba**
```
conda update -n base conda
conda install -n base conda-libmamba-solver
conda config -- set solver libmamba
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

## Predict keypoints with Sleap
You can use our pre-built models to pre


## Predict keypoints with MARS


## Calibration Videos


## Triangulate Keypoints 

