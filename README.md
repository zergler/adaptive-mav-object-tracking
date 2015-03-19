# Drone Project

Graduate research project involving the Parrot AR 2.0 drone.

One application written in node js creates an http server and serves the png images from the Parrot onto a port (9000 for now). Another applciation written in python uses the stream on the port to solve the computer vision problem using opencv and the reinforcement/imitation learning problem. The output of the python application is used by the node js application to tell the Parrot to takeoff, where to fly, etc. The python application returns a json string specifying a new action to take for this specific time-step and the json string is a dictionary with the following entries, for example:

query = {
  "X": 0.3,
  "Y": -0.9,
  "C": 0.0,
  "T": 0,
  "L": 0
}

where X corresponds to the left/right motion of the drone and Y corresponds to the up/down motion of the drone (negative means left/down). Also, T corresponds to takeoff, and L corresponds to land. The node js application listens for these dictionaries and when it receives one uses it along with the node-ar api to command the drone.
