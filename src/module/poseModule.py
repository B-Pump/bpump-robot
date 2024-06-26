from mediapipe import solutions
from cv2 import cvtColor, COLOR_BGR2RGB, FILLED, FONT_HERSHEY_PLAIN, MARKER_CROSS, line, circle, putText, drawMarker
from math import sqrt, atan2, degrees

class poseModule() :
    def __init__(self, mode=False, complexity=1, smooth_landmarks=True, enable_segmentation=False, smooth_segmentation=True, detectionCon=0.5, trackCon=0.5):
        """
        Initializing the class with specific parameters for model configuration and detection.

        :param mode: Pose model detection mode (defaults to False).
        :param complexity: Complexity level of the pose model (default to 1).
        :param smooth_landmarks: Enabling or disabling landmark smoothing (defaults to True).
        :param enable_segmentation: Enable or disable segmentation (defaults to False).
        :param smooth_segmentation: Enabling or disabling segmentation smoothing (defaults to True).
        :param detectionCon: Confidence threshold for detection (defaults to 0.5).
        :param trackCon: Confidence threshold for tracking (defaults to 0.5).
        """

        self.mode = mode 
        self.complexity = complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpDraw = solutions.drawing_utils
        self.mpPose = solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.complexity, self.smooth_landmarks, self.enable_segmentation, self.smooth_segmentation, self.detectionCon, self.trackCon)

    def findPose(self, video, draw=True):
        """
        Uses the pose model to detect pose in a video frame.

        :param video: The video frame in which to detect the pose.
        :param draw: Boolean indicating whether landmarks and connections should be drawn on the video frame (defaults to True).
        :return: The video frame with the landmarks and connections drawn.
        """

        self.results = self.pose.process(cvtColor(video, COLOR_BGR2RGB))
        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(video, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return video
    
    def findPosition(self, video, draw=True) -> list:
        """
        Extracts and returns the list of positions of the detected landmarks.

        :param video: The video frame from which to extract the positions of the landmarks.
        :param draw: Boolean indicating whether landmarks should be drawn on the video frame (default to True).
        :return: A list containing the positions of landmarks.
        """

        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = video.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])

                if draw:
                    circle(video, (cx, cy), 5, (0, 0, 255), FILLED)

        return self.lmList

    def findAngle(self, video, p1, p2, p3, draw=True) -> float:
        """
        Calculates the angle formed by three specified points.

        :param video: The video frame on which to draw the angle.
        :param p1, p2, p3: Landmark indices to calculate the angle (https://lc.cx/PLZ6m7).
        :param draw: Boolean indicating whether the angle should be drawn on the video frame (defaults to True).
        :return: The calculated angle in degrees.
        """

        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        angle = degrees(atan2(y3 - y2, x3 - x2) - atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
            if angle > 180:
                angle = 360 - angle
        elif angle > 180:
            angle = 360 - angle

        if draw:
            line(video, (x1, y1), (x2, y2), (255, 255, 255), 1)
            line(video, (x3, y3), (x2, y2), (255, 255, 255), 1)  
            circle(video, (x1, y1), 4, (0, 0, 255), FILLED)
            circle(video, (x2, y2), 4, (0, 0, 255), FILLED)
            circle(video, (x3, y3), 4, (0, 0, 255), FILLED)
            putText(video, str(int(angle)), (x2 + 10, y2 + 5), FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)

        return angle

    def findGravityPoint(self, video, draw=False):
        """
        Calculates the estimated center of mass (gravity point) of the detected human pose.

        :param video: The video frame containing the detected pose landmarks.
        :param draw: Boolean indicating whether to draw the estimated center of mass on the video frame (defaults to True).
        :return: A tuple containing the coordinates (x, y) of the estimated center of mass.
        """

        center_x = 0
        center_y = 0
        total_weight = 0
        relevant_landmarks = [0, 1, 12, 11, 23, 24, 26, 27]

        for landmark in self.lmList:
            id, cx, cy = landmark
            weight = 1 if id in relevant_landmarks else 0.5

            center_x += cx * weight
            center_y += cy * weight

            total_weight += weight

        if total_weight != 0:
            center_x /= total_weight
            center_y /= total_weight

            if draw:
                drawMarker(video, (int(center_x), int(center_y)), (255, 255, 255), MARKER_CROSS, markerSize=10, thickness=2)

        return center_x, center_y
    
    def getPixelSize(self, video, p1=31, p2=6, draw=False) -> float:
        """
        Calculates the pixel size between two specified landmarks and optionally draws the line on the video frame.

        :param video: The video frame in which to calculate the pixel size.
        :param draw: Boolean indicating whether to draw the distance line on the video frame (defaults to False).
        :return: The pixel size between the specified landmarks.
        """

        self.findPosition(video, False)

        if len(self.lmList) != 0:

            x1, y1 = self.lmList[p1][1:]
            x2, y2 = self.lmList[p2][1:]
            pixel_size = sqrt((x1 - x2)**2 + (y1 - y2)**2)

            if draw:
                line(video, (x2, y2), (x1, y1), (255, 0, 255), 1)
                putText(video, str(int(pixel_size)), (x2, y2 - 10), FONT_HERSHEY_PLAIN, 0.5, (255, 0, 255), 1)

            return pixel_size
        else:
            return 1