# PIMM
Implementation of PIMM algorithm
## Background
Aiming at the problems of low matching accuracy and slow matching speed of high-frequency trajectory data in complex urban road networks, this paper proposes a matching method based on path increment. This method is divided into two parts: combined filtering and incremental matching. Firstly, the road network is simplified through combined filtering, and then the incremental matching is carried out by taking the paths as increments. In the matching procedure, a comprehensive evaluation scheme of similarity based on distance factor and curvature is adopted.
## Installation
The program is develop using Python 3.6.9 and the request dependencies are list below:
- arcpy 2.8
- pandas 0.25.1
- time
- math
## Usage
"main.py" is the program entry point, and to run the demo, you only need to modify the "workspace" parameter in the "matchProcess" function.
The demo provides three test datasets sourced from GeoLife 1.3, each of which includes shapefile for roads and trajectories.
After running the program, it will automatically generate the filtered roads and matching results in the "workspace" directory. The results will be named "reslines".
