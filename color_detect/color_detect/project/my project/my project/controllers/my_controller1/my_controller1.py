from controller import Robot
class RobotController(Robot):
    def __init__(self):
        super().__init__()
        self.timestep = int(self.getBasicTimeStep())
        
        # إعداد العجلات
        self.left_wheel_front = self.getDevice("wheel2")
        self.left_wheel_rear = self.getDevice("wheel4")
        self.right_wheel_front = self.getDevice("wheel1")
        self.right_wheel_rear = self.getDevice("wheel3")
        for wheel in [self.left_wheel_front, self.left_wheel_rear, self.right_wheel_front, self.right_wheel_rear]:
            wheel.setPosition(float("inf"))
            wheel.setVelocity(0)

        # إعداد الكاميرا الجانبية
        self.side_camera = self.getDevice("camera1")  # تأكد أن الاسم مطابق لاسم الكاميرا في Webots
        self.side_camera.enable(self.timestep)

        # قائمة لتخزين الألوان المكتشفة
        self.detected_colors = []

        # حالة الروبوت
        self.is_collecting_colors = False  # لبدء جمع الألوان
        self.forward_speed = 3.0

    def detect_color(self):
        """
        يكتشف اللون باستخدام الكاميرا الجانبية.
        """
        image = self.side_camera.getImage()
        width = self.side_camera.getWidth()
        height = self.side_camera.getHeight()

        # قراءة بكسل في مركز الكاميرا
        center_pixel = [
            self.side_camera.imageGetRed(image, width, width // 2, height // 2),
            self.side_camera.imageGetGreen(image, width, width // 2, height // 2),
            self.side_camera.imageGetBlue(image, width, width // 2, height // 2),
        ]

        # طباعة قيم RGB للمراجعة
        print(f"RGB values: {center_pixel}")

        # تحديد اللون بناءً على قيم RGB
        if center_pixel == [241, 0, 0]:
            return "Red"
        elif center_pixel == [0, 241, 0]:
            return "Green"
        elif center_pixel == [24, 0, 241]:
            return "Blue"
        elif center_pixel == [241, 241, 0]:
            return "Yellow"
        elif center_pixel == [207, 207, 207]:  # اللون الأبيض
            return "White"
        return None

    def save_color(self, color):
        """
        يحفظ اللون المكتشف إذا كان جديدًا.
        """
        if color and color != "White" and (len(self.detected_colors) == 0 or self.detected_colors[-1] != color):
            self.detected_colors.append(color)
            print(f"Color detected and saved: {color}")

    def move_forward(self):
        """
        يتحرك الروبوت للأمام.
        """
        self.left_wheel_front.setVelocity(self.forward_speed)
        self.left_wheel_rear.setVelocity(self.forward_speed)
        self.right_wheel_front.setVelocity(self.forward_speed)
        self.right_wheel_rear.setVelocity(self.forward_speed)

    def stop(self):
        """
        يوقف الروبوت.
        """
        self.left_wheel_front.setVelocity(0)
        self.left_wheel_rear.setVelocity(0)
        self.right_wheel_front.setVelocity(0)
        self.right_wheel_rear.setVelocity(0)

    def loop(self):
        while self.step(self.timestep) != -1:
            # قراءة اللون من الكاميرا الجانبية
            color = self.detect_color()

            if color == "White":
                if not self.is_collecting_colors:
                    # تجاهل الأبيض والاستمرار في الحركة
                    print("Still on initial white, ignoring and moving forward.")
                elif len(self.detected_colors) >= 4:
                    # توقف عند قراءة الأبيض مرة أخرى بعد الألوان الأربعة
                    print("Second white detected after colors. Stopping robot.")
                    self.stop()
                    break
            else:
                # بدأ تخزين الألوان بعد تجاوز الأبيض الأول
                self.is_collecting_colors = True
                self.save_color(color)

            # تحرك للأمام
            self.move_forward()

        # طباعة ترتيب الألوان المكتشفة
        print("Detected color sequence:", self.detected_colors)

# تشغيل الكود
if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.loop()