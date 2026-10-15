FROM ros:jazzy

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ros-jazzy-mavros ros-jazzy-ament-mypy python3-pip python3-pygame python3-hamcrest \
 && rm -rf /var/lib/apt/lists/*
RUN /opt/ros/jazzy/lib/mavros/install_geographiclib_datasets.sh
RUN pip install --no-cache-dir --break-system-packages pymavlink

COPY src /ws/src
RUN . /opt/ros/jazzy/setup.sh \
 && cd /ws \
 && colcon build --symlink-install \
 && rm -rf log

COPY drone/streams.parm /app/streams.parm
