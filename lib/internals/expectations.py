import json

with open("./data/workouts.json", "r") as read_file:
    data = json.load(read_file)

def fetchPosition(exercise: str):
    parsed = data['workouts'][exercise]['position']
    positions = [(point['center_x'], point['center_y']) for point in parsed]

    return positions

def fetchInvert(exercice: str):
    """
    Checks if the exercise has the invertReward attribute associated with sugar

    :param exercise: The name of the exercise
    :return: True if an attribute is present, otherwise False
    """

    parsed = data['workouts'][exercice]
    if 'invertReward' not in parsed['sugar']:
        return False

    return True

def fetchAngles(exercice: str):
    """
    Retrieves the angles associated with an exercise

    :param exercise: The name of the exercise
    :return: A list of angles associated with the exercise
    """

    parsed = data['workouts'][exercice]
    angles = []
    for attribute in parsed:
        if 'angle' in parsed[attribute]:
            angles.append(parsed[attribute]['angle'])

    return angles

def lookup(exercice: str, pose):
    """
    Very simply, we are looking for an exercise to find the angles to look at, the min and max values

    :param exercise: The name
    :param pose: We pass the position to return an angle value
    :return: An array with the necessary lookup on each side
    """

    parsed = data['workouts'][exercice]
    if parsed is None:
        raise FileNotFoundError

    return [
        [
            pose[parsed['left']['angle']],
            parsed['left']['minAngle'],
            parsed['left']['maxAngle']
        ],
        [
            pose[parsed['right']['angle']],
            parsed['right']['minAngle'],
            parsed['right']['maxAngle']
        ]
    ]