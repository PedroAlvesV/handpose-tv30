from signal import default_int_handler


poses = []

# 0 fingers pose
p = {"FIST": [False]*5}
poses.append(p)

# 1 finger poses
p = {
    "POINT": [False, True, False, False, False],
    "THUMBS": [True, False, False, False, False],
    "PINKY": [False, False, False, False, True]
}
poses.append(p)

# 2 fingers poses
p = {
    "PEACE": [False, True, True, False, False],
    "ROCK": [False, True, False, False, True],
    "SHAKA": [True, False, False, False, True],
    "LOSER": [True, True, False, False, False]
}
poses.append(p)

# 3 fingers poses
p = {
    "THREE": [False, True, True, True, False],
    "LOVE": [True, True, False, False, True]
}
poses.append(p)

# 4 fingers poses
p = {
    "FOUR": [False, True, True, True, True]
}
poses.append(p)

# 5 fingers poses
p = {"OPEN": [True]*5}
poses.append(p)

defined_poses = set()
for pose_class in poses:
    for pose in pose_class:
        defined_poses.add(pose)