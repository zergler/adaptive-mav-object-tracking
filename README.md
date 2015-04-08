# Drone Project

Graduate research project involving the Parrot AR 2.0 drone which implements
a reactive controller that is able to successfully avoid stationary
obstacles using the drone's onboard camera and sensors. The controller is learned
by imitating an expert in a finite number of test cases. This project is heavily
influenced by the work of Ross et al. [2], [3] and is an attempt to implement this
research in Python using OpenCV.

## Proposal

Visual based object tracking can be implemented successfully in unmanned aerial
vehicles using information from a single on-board camera. Similarly, monocular
obstacle avoidance is advantageous in situations where extra sensors, such as
state-of-the-art radar or lidar are unavailable or the additional weight of the sensors
would make flying unfeasible. The purpose of this project is to create a 
a system that allows a small quadrotor micro aerial vehicle to navigate
cluttered environments while tracking an object autonomously using a single
camera with techniques from reinforcement and imitation learning.

## Installation

Make sure you have the AR Parrot 2.0 drone (untested on 1.0 version). You can start by
first downloading this repo. Change the install directory to whatever you want.

```
cd ~/
git clone http://github.com/zergler/drone-project
```

Next make sure you have the necessary programs installed. For example, on Arch Linux using pacaur for
installing AUR packages, do the following (making sure to install all dependecies).

```
pacaur -S nodejs python2 python2-numpy opencv
```

This package uses felixge's node-ar-drone package. Once you install node js though you can install this package
easily with npm.

```
npm install git://github.com/felixge/node-ar-drone.git
```

## How-To

Still in development.

## Background Information

### DAgger Algorithm

The Parrot's reactive controller will be learned using the DAgger (dataset aggregation)
algorithm developed by Ross et al. in [2]. Because the learner’s predictors affect future input during
execution of the learned policy, independent and identically distributed assumptions about the data
are violated. Because of this, algorithms that train under this assumption achieve poor performance
in practice [1]. This restriction is circumvented by the DAgger algorithm, since it trains a regressor
on the aggregate of the data that it has seen.

The algorithm can be described as follows. First the dataset D is empty and the initial policy is
chosen to be the expert policy (in general, any policy in the policy class may be used). Then for a
given number of iterations N, a new policy which is the combination of the expert's policy and the
last learned policy is executed for a given set of trajectories involving T time steps. Then the
dataset composed of the states the new policy visited as well as the expert’s actions under that
policy are collected and aggregated with the whole dataset. Finally, a new policy is trained on D. After
the last iteration, the best policy that works on new data is returned.

## References

[1] Vlachos, A. (2012) An investigation of imitation learning algorithms for structured prediction. In Proceed-
ings of the European Workshop on Reinforcement Learning (EWRL), pp. 143154.

[2] Ross, S & Gordon, G. & and Bagnell J.A. (2011) A reduction of imitation learning and structured prediction
to no-regret online learning. In International Conference on Artificial Intelligence and Statistics (AISTATS).

[3] Ross, S. & Melik-Barkhudarov, N. & Shankar, K.S. & Wendel, A. & Dey, D. & Bagnell, J.A. & Hebert, M.
(2013) Learning monocular reactive UAV control in cluttered natural environments. In International Conference
on Robotics and Automation (ICRA)
