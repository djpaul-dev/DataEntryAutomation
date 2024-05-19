#!/bin/bash

docker run -v $PWD:/workdir ghcr.io/streetsidesoftware/cspell:latest $1 --show-suggestions --quiet --unique