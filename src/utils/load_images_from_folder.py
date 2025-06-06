import pygame
import os

def load_images_from_folder(folder_path):
    images = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith('.png'):
            full_path = os.path.join(folder_path, filename)
            img = pygame.image.load(full_path).convert_alpha()
            images.append(img)
    return images