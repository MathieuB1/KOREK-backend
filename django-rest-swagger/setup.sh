#!/bin/bash
docker build . -t swagger
docker run -p 80:8000 -v $(pwd):/code swagger
