from controller import Robot

YOUBOT_MAX_VELOCITY = 14.0  # Maximum velocity of the YouBot

def range_conversion(s_start, s_end, d_start, d_end, value):
    """
    Map a value from one range to another.
    """
    ratio = (value - s_start) / (s_end - s_start)
    return d_start + (d_end - d_start) * ratio

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, error, delta_time):
        self.integral += error * delta_time
        derivative = (error - self.previous_error) / delta_time
        self.previous_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

class RobotController(Robot):
    def __init__(self):
        super().__init__()
        self.timestep = int(self.getBasicTimeStep())
        self.sensors = [self.getDevice(f"lfs{i}") for i in range(8)]
        self.weights = [-3000, -1000, 1000, 3000, -5000, 5000, -359, 359]
        for sensor in self.sensors:
            sensor.enable(self.timestep)

        # Initialize motors
        self.left_wheel_front = self.getDevice("wheel2")
        self.left_wheel_rear = self.getDevice("wheel4")
        self.right_wheel_front = self.getDevice("wheel1")
        self.right_wheel_rear = self.getDevice("wheel3")
        for wheel in [self.left_wheel_front, self.left_wheel_rear, self.right_wheel_front, self.right_wheel_rear]:
            wheel.setPosition(float("inf"))
            wheel.setVelocity(0)

        # PID Controller for turns
        self.pid = PIDController(kp=0.5, ki=0.0, kd=0.1)

        # State variables
        self.moving_backward = False
        self.turning = False
        self.turn_lock = False
        self.backward_steps = 0
        self.backward_step_target = 0  # Set when starting backward movement

    def get_sensors_value(self):
        value = 0
        active_sensors = 0
        for index, sensor in enumerate(self.sensors):
            if sensor.getValue() > 800:  # Adjust this threshold based on your sensor calibration
                value += self.weights[index]
                active_sensors += 1
        return value if active_sensors > 0 else None

    def set_motors_velocity(self, left, right):
        self.left_wheel_front.setVelocity(left)
        self.left_wheel_rear.setVelocity(left)
        self.right_wheel_front.setVelocity(right)
        self.right_wheel_rear.setVelocity(right)

    def correct_turn(self, velocity):
        """
        Use PID to adjust the robot's position after a turn.
        """
        self.turning=True
        delta_time = self.timestep / 1000.0
        error = self.get_sensors_value()
        if error is not None:
            
            correction = self.pid.compute(error, delta_time)
            left_velocity = velocity - correction/1000
            right_velocity = velocity + correction/1000
            self.set_motors_velocity(left_velocity, right_velocity)
            print(f"Correcting Turn: Error={error}, Correction={correction}, Left Velocity={left_velocity}, Right Velocity={right_velocity}")
        else:
            print("No line detected during correction.")

    def move_backward(self, velocity, steps):
        value = self.get_sensors_value()
        print(f"Sensor Value: {value}")
        if not self.moving_backward:
            self.backward_steps = 0
            self.backward_step_target = steps
            self.moving_backward = True
            print(f"Starting to move backward for {steps} steps.")

        if self.backward_steps < self.backward_step_target:
            self.set_motors_velocity(-velocity, -velocity)
            self.backward_steps += 1
            print(f"Moving backward: Step {self.backward_steps}/{self.backward_step_target}")
        else:
            print("Backward movement completed.")
          #  self.moving_backward = False
           # self.moving_backward = False
            if value >= 359:  # Sharp left turn detected
                 #   print("Sharp left turn detected. Executing left turn.")
                    self.turning = True
                    self.turn_lock = True
                    self.moving_backward = False
                    self.run_wheels_steering(-70, velocity) 
                    
            elif value <= -359:  # Sharp right turn detected
                    print("Sharp right turn detected. Executing right turn.")
                    self.turning = True
                    self.turn_lock = True
  
                    delta_time = self.timestep / 1000.0
                    error = self.get_sensors_value()/100
                    if error is not None:
            
                       correction = self.pid.compute(error, delta_time)
                       left_velocity = velocity + correction/1000
                       right_velocity = velocity -correction/1000
                       self.set_motors_velocity(left_velocity, right_velocity)
                   #    print(f"  Left Velocity: {left_velocity}, Right Velocity: {right_velocity}")
                      
                       self.moving_backward = False
                    
                    print(value)
 
                    
                

    def run_wheels_steering(self, steering, velocity):
        """
        Run the wheels with a steering angle and velocity.
        Steering values represent the direction of the turn (-70 to 70), with:
        -70 being sharp left turn
        70 being sharp right turn
        """
        if steering <= -70 or steering >= 70:  # Turn initiated
            self.correct_turn(velocity)
        else:  # Regular steering (line following)
            left_velocity = range_conversion(0, 100, velocity, -velocity, steering)
            right_velocity = range_conversion(0, -100, velocity, -velocity, steering)
            self.left_wheel_front.setVelocity(left_velocity)
            self.left_wheel_rear.setVelocity(left_velocity)
            self.right_wheel_front.setVelocity(right_velocity)
            self.right_wheel_rear.setVelocity(right_velocity)

    def line_follow_step(self, velocity=YOUBOT_MAX_VELOCITY):
      value = self.get_sensors_value()
      print(f"Sensor Value: {value}")
 
      if self.moving_backward  :
              
                self.move_backward(velocity=2, steps=740)  # Specify the number of steps for backward movement
       
                return  
                
      if value is None:  # Handle no line detected
            if  not self.moving_backward and self.turning==False :
                self.move_backward(velocity=2, steps=740)
                return       
            elif self.moving_backward    : 
                self.run_wheels_steering(0, velocity)
                return
      if   self.moving_backward==False and value is not None  and   self.turning==False :
     
        if value > 1500:  # Sharp left turn detected
            print("Sharp left turn detected while moving forward.")
            self.run_wheels_steering(-70, velocity)
            self.turning=False
        elif value < -1000:  # Sharp right turn detected
            print("Sharp right turn detected while moving forward.")
            self.run_wheels_steering(70,- velocity)
            self.turning=False
        else:  # Regular line-following
            steering = range_conversion(-4000, 4000, -30, 30, value)
            self.run_wheels_steering(steering, velocity)

    #   if self.turning:
    #     if value is None or abs(value) 800:  # Stop turning if no line or weak detection
    #         print("Stopping turn due to low sensor values.")
    #         self.turning = False
    #         self.set_motors_velocity(0, 0)  # Stop motors briefly
    #     else:
    #         self.correct_turn(velocity)  # Continue correcting turn
    #     return



    def loop(self):
        while self.step(self.timestep) != -1:
            self.line_follow_step(2)

# Instantiate and start the robot controller
if __name__ == "__main__":
    r = RobotController()
    r.loop()
