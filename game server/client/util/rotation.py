import math


def rot_ratio(angle) -> list:
    rot = angle / 180 * math.pi

    AC = 1
    AB = AC * math.cos(rot)
    BC = AC * math.sin(rot)

    return [AB, BC]


def find_line_pos(pos1, pos2, divider, interpolation):
    disx = pos2[0] - pos1[0]
    disy = pos2[1] - pos1[1]

    pxlsx = disx / divider * interpolation
    pxlsy = disy / divider * interpolation

    return [pos1[0] + pxlsx, pos1[1] + pxlsy]



