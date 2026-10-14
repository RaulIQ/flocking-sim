FROM ros:jazzy

RUN apt-get update \
 && apt-get install -y --no-install-recommends ros-jazzy-mavros python3-pip python3-pygame \
 && rm -rf /var/lib/apt/lists/*
RUN /opt/ros/jazzy/lib/mavros/install_geographiclib_datasets.sh
RUN pip install --no-cache-dir --break-system-packages pymavlink

COPY msgs /ws/src
RUN . /opt/ros/jazzy/setup.sh \
 && cd /ws \
 && colcon build --packages-select flocking_msgs \
 && rm -rf build log

COPY drone/streams.parm /app/streams.parm
