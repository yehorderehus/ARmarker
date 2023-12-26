import subprocess
import random

def create_input():
    """
    When changing the aruco dictionary (type of marker),
    consider changing the range of the random number
    0: 4X4_50: 0-49
    1: 4X4_100: 0-99
    2: 4X4_250: 0-249
    3: 4X4_1000: 0-999
    4: 5X5_50: 0-49
    5: 5X5_100: 0-99
    6: 5X5_250: 0-249
    7: 5X5_1000: 0-999
    8: 6X6_50: 0-49
    9: 6X6_100: 0-99
    10: 6X6_250: 0-249
    11: 6X6_1000: 0-999
    12: 7X7_50: 0-49
    13: 7X7_100: 0-99
    14: 7X7_250: 0-249
    15: 7X7_1000: 0-999
    16: ARUCO_ORIGINAL: ?
    17: APRILTAG_16h5: ?
    18: APRILTAG_25h9: ?
    19: APRILTAG_36h10: ?
    20: APRILTAG_36h11: ?
    """
    
    # Predefined random marker ID
    marker_id = random.randint(0, 999)

    inputs = [
        "11",  # Answer to the type of marker
        f"{marker_id}",  # Answer to the marker ID
        "90",  # Answer to the total side length
        "1",   # Answer to the marker thickness
        "10",  # Answer to the white margin width
        "0.4", # Answer to the groove depth
        "2"    # Answer to the layer height
    ]

    indented_inputs = "\n".join(f"  {input}" for input in inputs)
    return indented_inputs

def run_generate_aruco():
    command = "python generate_aruco.py"

    try:
        inputs = create_input()
        print("Inputs:")
        print(inputs)
        subprocess.run(command, shell=True, check=True, text=True, input=inputs)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_generate_aruco()
