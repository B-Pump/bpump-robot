import json

with open("./data/workouts.json", "r") as read_file:
    data = json.load(read_file)

def fetchSugar(exercice):
    parsed = data['workouts'][exercice]
    return parsed['sugar']['title']

def fetchInvert(exercice):
    parsed = data['workouts'][exercice]
    if 'invertReward' not in parsed['sugar']:
        return False
    return True

def fetchAngles(exercice):
    parsed = data['workouts'][exercice]
    angles = []
    for attribute in parsed:
        if 'angle' in parsed[attribute]:
            angles.append(parsed[attribute]['angle'])
    return angles

def fetchPositions(exercice):
    parsed = data['workouts'][exercice]['position']
    positions = [(point['center_x'], point['center_y']) for point in parsed]
    return positions

def lookup(exercice, pose):
    parsed = data['workouts'][exercice]
    if parsed == None:
        raise FileNotFoundError
    return [
        [
            getattr(pose, parsed['left']['angle']),
            parsed['left']['minAngle'],
            parsed['left']['maxAngle']
        ],
        [
            getattr(pose, parsed['right']['angle']),
            parsed['right']['minAngle'],
            parsed['right']['maxAngle']
        ]
    ]