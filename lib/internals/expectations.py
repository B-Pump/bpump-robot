import json

with open("./data/workouts.json", "r") as read_file:
    data = json.load(read_file)

def fetchPosition(exercise: str):
    parsed = data['workouts'][exercise]['position']
    positions = [(point['center_x'], point['center_y']) for point in parsed]

    return positions