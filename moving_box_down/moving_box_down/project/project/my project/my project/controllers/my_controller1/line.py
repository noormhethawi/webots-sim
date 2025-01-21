from controller import Robot

YOUBOT_MAX_VELOCITY = 14.0  # Maximum velocity of the YouBot

def range_conversion(s_start, s_end, d_start, d_end, value):
    """
    Map a value from one range to another.
    Example: 50 from range 0-200 to range -50-50 -> -25
    """
    ratio = (value - s_start) / (s_end - s_start)
    return d_start + (d_end - d_start) * ratio

class RobotController(Robot):
    def __init__(self):
        super().__init__()
        self.timestep = int(self.getBasicTimeStep())

        # Initialize YouBot wheels
        self.left_wheel_front = self.getDevice("wheel2")
        self.left_wheel_rear = self.getDevice("wheel4")
        self.right_wheel_front = self.getDevice("wheel1")
        self.right_wheel_rear = self.getDevice("wheel3")

        # Set wheels to velocity control mode
        for wheel in [self.left_wheel_front, self.left_wheel_rear, self.right_wheel_front, self.right_wheel_rear]:
            wheel.setPosition(float("inf"))
            wheel.setVelocity(0)

        # Initialize line-following sensors
        self.sensors = [self.getDevice(f"lfs{i}") for i in range(4)]  # Adjust sensor names as needed
        self.weights = [-3000, -1000, 1000, 3000]  # Adjust weights based on sensor position

        for sensor in self.sensors:
            sensor.enable(self.timestep)

        self.step(self.timestep)

        # Initialization for line searching
        self.searching = False
        self.search_time = 0

    def get_sensors_value(self):
        """
        Reads the sensor values and returns a weighted sum.
        Returns None if no sensor detects the line.
        """
        value = 0
        active_sensors = 0

        for index, sensor in enumerate(self.sensors):
            sensor_value = sensor.getValue()
            print(f"Sensor {index} value: {sensor_value}")  # Debugging sensor values
            if sensor_value > 600:  # Adjust threshold based on calibration
                value += self.weights[index]
                active_sensors += 1

        return value if active_sensors > 0 else None

    def run_wheels_steering(self, steering, velocity=YOUBOT_MAX_VELOCITY):
        """
        Adjust wheel velocities based on steering value.
        """
        right_velocity = velocity if steering < 0 else range_conversion(0, 100, velocity, -velocity, steering)
        left_velocity = velocity if steering > 0 else range_conversion(0, -100, velocity, -velocity, steering)

        print(f"Steering: {steering}, Left Velocity: {left_velocity}, Right Velocity: {right_velocity}")

        self.left_wheel_front.setVelocity(left_velocity)
        self.left_wheel_rear.setVelocity(left_velocity)
        self.right_wheel_front.setVelocity(right_velocity)
        self.right_wheel_rear.setVelocity(right_velocity)

    def line_follow_step(self, velocity=YOUBOT_MAX_VELOCITY):
        """
        Execute one step of the line-following algorithm with turn detection.
        """
        value = self.get_sensors_value()
        
        if value is None:
            if not self.searching:
                print("No line detected, starting search.")
                self.searching = True
                self.search_time = 0  # Reset the search timer

            self.search_time += 1
            if self.search_time > 100:  # Timeout after 100 steps
                print("Search timeout reached, stopping robot.")
                self.run_wheels_steering(0, 0)
                return

        # Turn Detection: Check if only one sensor is detecting the line (sharp turns)
        if value < -2000:  # Line is heavily to the right
            print(f"Sharp left turn detected +{value}.")
            self.run_wheels_steering(steering=-70, velocity=velocity)  # Adjust this value for sharp right
            return
        elif value > 2000:  # Line is heavily to the left
            print(f"Sharp right turn detected.+{value}")
            self.run_wheels_steering(steering=70, velocity=velocity)  # Adjust this value for sharp left
            return
        else : 
            print(value) 
        
        # Regular line-following steering
        steering = range_conversion(-900, 900, 30, -30, value)
        print(f"Weighted Value: {value}, Steering: {steering}")
        self.run_wheels_steering(steering, velocity)

    def line_following(self, velocity=YOUBOT_MAX_VELOCITY):
        """
        Continuously perform line-following.
        """
        while self.step(self.timestep) != -1:
            self.line_follow_step(velocity)

    def print_sensor_value(self):
        """
        Debug method to print the sensor readings.
        """
        while self.step(self.timestep) != -1:
            print(f"Sensor Values: {[sensor.getValue() for sensor in self.sensors]}")

# Instantiate and start the robot controller
if __name__ == "__main__":
    r = RobotController()
    r.line_following(2)  # Start line-following with velocity 2
