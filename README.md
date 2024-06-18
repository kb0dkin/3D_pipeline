# 3D_pipeline

This pipeline steps through 3D markerless motion tracking for our food handling tasks. It uses a combination of 2D motion tracking systems and [Anipose](github.com/lambdaloop/anipose). It also includes tools to use AWS labeling services to put together initial training sets, like in [MARS](github.com/neuroethology/MARS_developer).

## Installation and Required Tools
1. 2D markerless motion tracking can be done using either [MARS developer](github.com/neuroethology/MARS_developer) or [SLEAP](sleap.ai)
2. [Anipose](github.com/lambdaloop/anipose) for camera calibration and marker triangulation

All required tools can be installed using the provided Conda file. Refer to [Anaconda's documentation](https://docs.anaconda.com/miniconda/) for installation and usage of Conda.

To install the Sleap-based toolchain:
```
conda env create -n pipeline_3D -f pipeline_sleap
```


To install the Sleap-based toolchain:
```
conda env create -n pipeline_3D -f pipeline_MARS
```
