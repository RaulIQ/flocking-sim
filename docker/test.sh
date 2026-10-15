#!/bin/bash
set -e
cd "$(dirname "$0")"
docker compose run --rm --no-deps --entrypoint bash uav1 -c \
    "source /opt/ros/jazzy/setup.bash && source /ws/install/setup.bash && cd /ws/src/flocking_ros && PYTHONPATH=/app/flocking:\$PYTHONPATH SDL_VIDEODRIVER=dummy MYPY_CACHE_DIR=/tmp/mypy python3 -m pytest -q -p no:cacheprovider test $*"
