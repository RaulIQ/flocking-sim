#!/bin/bash
set -e
cd "$(dirname "$0")"
docker compose run --rm --no-deps --entrypoint bash uav1 -c \
    "source /opt/ros/jazzy/setup.bash && source /ws/install/setup.bash && cd /app/flocking && PYTHONPATH=.:docker/drone/nodes:docker/ground/nodes:\$PYTHONPATH SDL_VIDEODRIVER=dummy python3 -m pytest -q -p no:cacheprovider docker/drone/tests docker/ground/tests $*"
