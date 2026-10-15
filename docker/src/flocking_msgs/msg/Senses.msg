# Everything one drone is told in one tick besides its own motion, all of it in its own frame:
# whether it leads, its neighbours, the nearest point of every wall and what the pilot asks
std_msgs/Header header
bool leader
Range[] ranges
Bearing[] bearings
Role[] roles
geometry_msgs/Point[] obstacles
geometry_msgs/Twist request
