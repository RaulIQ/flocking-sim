FROM jazzy-gz

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
 && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/ArduPilot/ardupilot_gazebo /opt/ardupilot_gazebo/src \
 && . /opt/ros/jazzy/setup.sh \
 && cmake -S /opt/ardupilot_gazebo/src -B /opt/ardupilot_gazebo/build -DCMAKE_BUILD_TYPE=RelWithDebInfo \
 && cmake --build /opt/ardupilot_gazebo/build -j"$(nproc)"

ENV GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ardupilot_gazebo/build
ENV GZ_SIM_RESOURCE_PATH=/opt/ardupilot_gazebo/src/models:/opt/ardupilot_gazebo/src/worlds
