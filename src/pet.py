# pet.py
from src.utils.load_images_from_folder import load_images_from_folder

import pygame
import os
import win32gui
import win32con
import win32api


class DesktopPet:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 1000), pygame.NOFRAME)

        pygame.init()
        # 加载宠物图片
        # self.image = pygame.image.load(os.path.join("assets", "pet", "pic", "pet_test.png"))
        # self.rect = self.image.get_rect()
        
        # 创建透明窗口
        # self.screen = pygame.display.set_mode((self.rect.width, self.rect.height), pygame.NOFRAME)
        pygame.display.set_caption("Desktop Pet")
        
        # 设置窗口透明
        self.transparent()
        # 
    # 设置透明(不知道为什么没用)
    def transparent(self):
        hwnd = pygame.display.get_wm_info()["window"]
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED)

        win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 0, win32con.LWA_COLORKEY)
    
    def update(self):
        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()

def pet_run():
    pet = DesktopPet()
        
    running = True
    pet.__init__()
    frames = load_images_from_folder(r'assets\image')
    frame_index = 0
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        # pet.update()
        # 刷新去掉之前的帧
        pet.screen.fill((0, 0, 0))
        # 加载新的帧
        frame = frames[frame_index]
        # 显示帧 居中显示
        pet.screen.blit(frame, (pet.screen.get_width() // 2 - frame.get_width() // 2,
                            pet.screen.get_height() // 2 - frame.get_height() // 2))
        # 切换帧 这里为循环播放
        frame_index = (frame_index + 1) % len(frames)

        pygame.display.flip()
        clock.tick(6)  # 每秒播放 6 帧
