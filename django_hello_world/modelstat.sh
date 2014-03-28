#!/bin/bash

filename=$(date +"%m_%d_%Y").dat
python ./manage.py modelstat 2>$filename
