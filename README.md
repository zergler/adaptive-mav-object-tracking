# Drone Project

Graduate research project involving the Parrot AR 2.0 drone.

Visual based object tracking can be implemented successfully in unmanned aerial
vehicles using information from a single on-board camera. Similarly, monocu-
lar obstacle avoidance is advantageous in situations where extra sensors, such as
state-of-the-art radar or lidar are unavailable or the additional weight of the sen-
sors would make flying unfeasible. The purpose of this project is to create a 
a system that allows a small quadrotor micro aerial vehicle to navigate
cluttered environments while tracking an object autonomously using a single
camera with techniques from reinforcement and imitation learning.

One application written in node js creates an http server and serves the png
images from the Parrot onto a port (9000 for now). Another application written
in python uses the stream on the port to solve the computer vision problem
using opencv and the reinforcement/imitation learning problem. The output of
the python application is piped to the node js application to tell the Parrot to
takeoff, where to fly, etc. The python application returns a json string
specifying a new action to take for this specific time-step and the json string
is a dictionary with the following entries, for example:

query = {
  "X": 0.3,
  "Y": -0.9,
  "C": 0.0,
  "T": 0,
  "L": 0
}

where X corresponds to the left/right motion of the drone and Y corresponds to
the up/down motion of the drone (negative means left/down). Also, T corresponds
to takeoff, and L corresponds to land. The node js application listens for these
dictionaries and when it receives one uses it along with the node-ar API to
command the drone.
