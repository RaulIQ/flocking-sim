from config import defaults, kinematics
from simulator.loop import Flight

if __name__ == "__main__":
    Flight(defaults(), kinematics(defaults())).run()
