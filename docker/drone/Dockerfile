FROM ros:jazzy

RUN apt-get update \
 && apt-get install -y --no-install-recommends ros-jazzy-mavros \
 && rm -rf /var/lib/apt/lists/*
RUN /opt/ros/jazzy/lib/mavros/install_geographiclib_datasets.sh

COPY streams.parm /app/streams.parm
COPY start.sh /app/start.sh
ENTRYPOINT ["/app/start.sh"]
