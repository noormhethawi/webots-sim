from controller import Robot

# إعداد الروبوت
TIME_STEP = 32
robot = Robot()

# إعداد عجلات الروبوت
wheels = [
    robot.getDevice('wheel1'),  # عجلة 1
    robot.getDevice('wheel2'),  # عجلة 2
    robot.getDevice('wheel3'),  # عجلة 3
    robot.getDevice('wheel4')   # عجلة 4
]

# ضبط المحركات على الوضع اللانهائي
for wheel in wheels:
    wheel.setPosition(float('inf'))
    wheel.setVelocity(0)

# إعداد GPS وبوصلة
gps = robot.getDevice('gps')
gps.enable(TIME_STEP)

compass = robot.getDevice('compass')
compass.enable(TIME_STEP)

# الأماكن المعلومة بالإحداثيات (X, Z) على الرقعة
places = {
    "start": (0, 0),          # نقطة البداية
    "yellow_zone": (1, 2),    # المنطقة الصفراء
    "red_zone": (2, -2),      # المنطقة الحمراء
    "green_zone": (-2, -2),   # المنطقة الخضراء
    "blue_zone": (-1, 2),     # المنطقة الزرقاء
    "wall_center": (0, 4)     # مركز الحائط
}

# تابع لحساب المسافة بين نقطتين
def calculate_distance(x1, z1, x2, z2):
    return ((x2 - x1)**2 + (z2 - z1)**2)**0.5

# تابع لتحريك الروبوت نحو الهدف
def move_to_target(target_x, target_z):
    while robot.step(TIME_STEP) != -1:
        # قراءة موقع الروبوت الحالي
        position = gps.getValues()
        current_x, current_z = position[0], position[2]

        # حساب المسافة إلى الهدف
        distance = calculate_distance(current_x, current_z, target_x, target_z)

        # التوقف إذا وصل الروبوت إلى الهدف
        if distance < 0.1:
            for wheel in wheels:
                wheel.setVelocity(0)
            print("Reached target:", (target_x, target_z))
            break

        # حساب الاتجاه نحو الهدف
        direction_x = target_x - current_x
        direction_z = target_z - current_z

        # سرعة الحركة
        speed = 3.0
        wheels[0].setVelocity(speed * (direction_x - direction_z))
        wheels[1].setVelocity(speed * (-direction_x - direction_z))
        wheels[2].setVelocity(speed * (direction_x + direction_z))
        wheels[3].setVelocity(speed * (-direction_x + direction_z))

# النقطة الهدف
target_place = "yellow_zone"  # اختاري أي منطقة من places
target_x, target_z = places[target_place]

# استدعاء التابع للتحرك نحو الهدف
move_to_target(target_x, target_z)
