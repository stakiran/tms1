#!/bin/bash

input_folder=scb
output_folder=html

mkdir $input_folder
mkdir $output_folder

python3 dobu.py --input-directory $input_folder --output-directory $output_folder
cp stylesheet.css $output_folder
