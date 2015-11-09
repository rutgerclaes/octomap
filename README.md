# Python OctoMap implementation

This is a python based implementation of the [OctoMap](http://octomap.github.io) datastructure
described in [OctoMap: An Efficient Probabilistic 3D Mapping Framework Based on Octrees]
(http://www.informatik.uni-freiburg.de/~hornunga/pub/hornung13auro.pdf).  If you want to use this
library, checkout the OctoMap project first.

## Project goals

1. See whether python based implementation of an octomap is feasible.
2. See whether octomap principles could be of use in our autonomic drone research.

## Future work

### Raytracing
This library only makes sense if you can do some sort of raytracing.  Remains future work though.

### Observation based API 
Ideally, the library offers an API that allows you to do `record distance d measured from point (x,y,z) with 
sensor inaccuracy i in direction (yaw,pitch,roll)`.  This would then update the odds of occupancy around the
measured distance.

### Benchmarking the functional interface
The current implementation doesn't store any of the geometry data in the `OccupancyOctoNodes`.  It simply passes
all required information as arguments down the chain.  This should lead to some memory consumption improvements.
It would be interesting to see the computational penalty involved though.