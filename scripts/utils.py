import pygame
import os
from settings import BASE_IMAGE_PATH


def load_image(path):
    img = pygame.image.load(BASE_IMAGE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMAGE_PATH + path):
        images.append(load_image(path + "/" + img_name))
    return images


class Animation:
    def __init__(self, images, image_duration=5, loop=True):
        self.images = images
        self.loop = loop
        self.image_duration = image_duration
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.image_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.image_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.image_duration * len(self.images) - 1)
            if self.frame >= self.image_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.image_duration)]
