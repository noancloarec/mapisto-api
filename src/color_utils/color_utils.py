import skimage.color
import numpy as np
import logging

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)]) / 255

def colour_distance(hex_1, hex_2):
    # logging.error(f'rgb1 : {hex_to_rgb(hex_1)}     rgb2 : {hex_to_rgb(hex_2)}')
    [[lab1, lab2]] = skimage.color.rgb2lab([[hex_to_rgb(hex_1), hex_to_rgb(hex_2)]])
    # logging.error(f'lab1 : {hex_to_rgb(hex_1)}     lab2 : {hex_to_rgb(hex_2)}')
    return np.linalg.norm(lab1 - lab2)

def colours_roughly_equal(hex_1, hex_2):
    return colour_distance(hex_1, hex_2) < 15