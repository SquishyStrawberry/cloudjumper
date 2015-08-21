#!/usr/bin/env bash

usage="Usage: $0 INSTALL_DIRECTORY"
origin=$(pwd)

# TODO Find a better way to check for pip
if hash pip3; then
    echo "Found pip3"
    good_pip=pip3
elif hash pip; then
    echo "Found pip"
    good_pip=pip
else
    echo "Could not find pip, please speak to the developer for instructions."
    exit 1
fi

# Sanity check
# TODO Convert this to new syntax
if [[ -z $1 ]]; then
    echo $usage
    exit 1
fi

# Install the modules
# TODO Find a better way to check for root requirements
$good_pip install -e $origin 
if [[ $? == 1 ]]; then
    sudo $good_pip install -e $origin
fi

# Go to the installation directory
mkdir -p $1
cd $1

# Actually create the files
# TODO Provide option to just copy instead of link
ln -s ${origin}/_modules ${origin}/modules.py .
cp ${origin}/config.json .

