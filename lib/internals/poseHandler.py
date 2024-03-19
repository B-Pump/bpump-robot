class poseHandler:
    def poseHandler(self, img, detector, joint_names):
        """
        Manipulates the detected pose and returns a dictionary of joint angles

        :param img: The input image
        :param detector: The type of detector
        :param joint_names: The list of joints
        :return: A dictionary containing joint names as keys and angles as values
        """

        joint_indices = {
            "angleLeftArm": (12, 14, 16),
            "angleLeftHip": (12, 24, 26),
            "angleLeftLeg": (24, 26, 28),
            "angleLeftFoot": (26, 28, 32),
            "angleRightArm": (11, 13, 15),
            "angleRightHip": (11, 23, 25),
            "angleRightLeg": (23, 25, 27),
            "angleRightFoot": (25, 27, 31)
        }
        angles = {joint: detector.findAngle(img, *joint_indices[joint]) for joint in joint_names}

        return angles