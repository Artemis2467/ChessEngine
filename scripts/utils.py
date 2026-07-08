import os
import pygame

ROOT_PATH = 'pieces'

def load_images(path, tile_size):
    images = {}
    for image_name in os.listdir(ROOT_PATH + '/' + path):
        piece_name = "".join(list(image_name)[:-4])
        images[piece_name] = pygame.transform.scale(pygame.image.load(ROOT_PATH + "/" + path + '/' + image_name), (tile_size, tile_size)).convert_alpha()
    return images

def load_image(path, tile_size=90)->pygame.Surface:
    image = pygame.transform.scale(pygame.image.load(ROOT_PATH + "/" + path), (tile_size, tile_size)).convert_alpha()
    return image