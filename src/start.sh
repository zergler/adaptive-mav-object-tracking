#!/bin/bash

#./fly.py -v annotate 1 1
#./fly.py -v train 1 tikhonov
./fly.py -v exec localhost:9000 localhost:9001 tikhonov 1 1
