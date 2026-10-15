FROM jazzy-gz

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
 && rm -rf /var/lib/apt/lists/*
# @todo #4:30min The plugin is built from the commit of ArduPilot/ardupilot_gazebo#181,
#  since main shares one address among every copter and sends their state to one
#  container only. Return to main once #181 or #166 is merged there.
RUN git init -q /opt/ardupilot_gazebo/src \
 && git -C /opt/ardupilot_gazebo/src fetch -q --depth 1 https://github.com/ArduPilot/ardupilot_gazebo 78c833951957bdf3af0d3dbfcb17155214dfb0e2 \
 && git -C /opt/ardupilot_gazebo/src checkout -q FETCH_HEAD \
 && . /opt/ros/jazzy/setup.sh \
 && cmake -S /opt/ardupilot_gazebo/src -B /opt/ardupilot_gazebo/build -DCMAKE_BUILD_TYPE=RelWithDebInfo \
 && cmake --build /opt/ardupilot_gazebo/build -j"$(nproc)"
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --break-system-packages --no-cache-dir pymavlink

ENV GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ardupilot_gazebo/build
ENV GZ_SIM_RESOURCE_PATH=/opt/ardupilot_gazebo/src/models:/opt/ardupilot_gazebo/src/worlds
