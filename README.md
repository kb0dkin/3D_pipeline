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
