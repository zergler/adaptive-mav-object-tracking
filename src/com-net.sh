#!/bin/bash
sudo netctl stop Parrot
sudo systemctl restart netctl-auto@wlp16s0.service
