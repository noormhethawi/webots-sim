from controller import Robot

# Create the Robot instance
robot = Robot()

# Get the time step of the current world
timestep = int(robot.getBasicTimeStep())

# Initialize arm motors
arm_motors = []
arm_motors.append(robot.getDevice("arm1"))  # Base rotation
arm_motors.append(robot.getDevice("arm2"))  # Shoulder
arm_motors.append(robot.getDevice("arm3"))  # Elbow
arm_motors.append(robot.getDevice("arm4"))  # Wrist 1
arm_motors.append(robot.getDevice("arm5"))  # Wrist 2

# Set maximum velocity for each arm motor
for motor in arm_motors:
    motor.setVelocity(0.5)

# Initialize arm position sensors
arm_sensors = []
for i in range(5):
    sensor = robot.getDevice(f"arm{i + 1}sensor")
    sensor.enable(timestep)
    arm_sensors.append(sensor)

# Initialize gripper motors
finger1 = robot.getDevice("finger::left")
finger2 = robot.getDevice("finger::right")

# Set maximum velocity for gripper motors
finger1.setVelocity(0.04)
finger2.setVelocity(0.04)

# Read minimum and maximum positions of the gripper motors
finger_min_position = finger1.getMinPosition()
finger_max_position = finger1.getMaxPosition()

# Function to wait until a motor reaches a specific position
def wait_until_motor_reaches(sensor, target_position, tolerance=0.01):
    while robot.step(timestep) != -1:
        if abs(sensor.getValue() - target_position) < tolerance:
            break

# Step 1: Rotate the arm base to the right to align with the box
print("Rotating arm base to the right to align with the box...")
arm_motors[0].setPosition(1.57)  # Rotate to the right (90 degrees)
wait_until_motor_reaches(arm_sensors[0], 1.57)

# Step 2: Lower the arm to the box position and open the gripper
print("Lowering the arm to the box position...")
arm_motors[1].setPosition(-0.5)  # Lower the arm to the box height
arm_motors[2].setPosition(-0.8)  # Reach forward to the box
arm_motors[3].setPosition(-1.5)  # Adjust wrist for picking
finger1.setPosition(finger_max_position)
finger2.setPosition(finger_max_position)
wait_until_motor_reaches(arm_sensors[3], -1.5)

# Step 3: Close the gripper to grab the box
print("Closing gripper to grab the box...")
finger1.setPosition(0.013)
finger2.setPosition(0.013)
robot.step(50 * timestep)

# Step 4: Lift the arm with the box
print("Lifting the arm with the box...")
arm_motors[1].setPosition(0.0)  # Lift the arm up
wait_until_motor_reaches(arm_sensors[1], 0.0)

# Step 5: Rotate the base to align with the target location
print("Rotating arm base to the target location...")
arm_motors[0].setPosition(0.0)  # Rotate back to center
wait_until_motor_reaches(arm_sensors[0], 0.0)

# Step 6: Lower the arm to place the box
print("Lowering the arm to place the box...")
arm_motors[1].setPosition(-0.6)  # Lower the arm near the target
arm_motors[2].setPosition(-0.4)  # Adjust forward reach
arm_motors[3].setPosition(-1.0)  # Adjust wrist for placing
wait_until_motor_reaches(arm_sensors[3], -1.0)

# Step 7: Open the gripper to release the box
print("Opening the gripper to release the box...")
finger1.setPosition(finger_max_position)
finger2.setPosition(finger_max_position)
robot.step(50 * timestep)

# Step 8: Return the arm to its resting position
print("Returning arm to resting position...")
arm_motors[1].setPosition(0.0)  # Lift the arm back up
arm_motors[2].setPosition(0.0)  # Reset forward reach
arm_motors[3].setPosition(0.0)  # Reset wrist angle
wait_until_motor_reaches(arm_sensors[1], 0.0)

print("Task completed successfully!")
