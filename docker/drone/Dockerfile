FROM ros:jazzy

RUN apt-get update \
 && apt-get install -y --no-install-recommends ros-jazzy-mavros python3-pip \
 && rm -rf /var/lib/apt/lists/*
RUN /opt/ros/jazzy/lib/mavros/install_geographiclib_datasets.sh
RUN pip install --no-cache-dir --break-system-packages pymavlink

COPY streams.parm /app/streams.parm
COPY start.sh /app/start.sh
ENTRYPOINT ["/app/start.sh"]
