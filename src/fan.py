import RPi.GPIO as IO # type: ignore
from time import sleep
from subprocess import run

IO.setwarnings(False)
IO.setmode (IO.BCM)
IO.setup(14, IO.OUT)
fan = IO.PWM(14, 100)
fan.start(0)

minTemp = 35
maxTemp = 60
minSpeed = 0
maxSpeed = 100

def get_temp():
    output = run(["vcgencmd", "measure_temp"], capture_output=True)
    temp_str = output.stdout.decode()

    try:
        result = float(temp_str.split("=")[1].split("\'")[0])
        # print(result) # debug purposes

        return result
    except (IndexError, ValueError):
        raise RuntimeError("Could not get temperature")
    
def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]

    return (delta2 * (n - range1[0]) / delta1) + range2[0]

while 1:
    temp = get_temp()

    if temp < minTemp:
        temp = minTemp
    elif temp > maxTemp:
        temp = maxTemp

    fan.ChangeDutyCycle(int(renormalize(temp, [minTemp, maxTemp], [minSpeed, maxSpeed])))

    sleep(5)