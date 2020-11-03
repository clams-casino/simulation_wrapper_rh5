ROS wrapped duckietown-gym which publishes images and subscribes to wheel commands and virtual joystick commands


# Usage

Set up docker compose containers and robot name for simulation according to instructions here:
https://docs.duckietown.org/daffy/duckietown-robotics-development/out/duckietown_simulation.html

Build it on the laptop. Following commands are run in the root directory of the repo
```
dts devel build -f 
```

Running it on the laptop
```
dts devel run
```