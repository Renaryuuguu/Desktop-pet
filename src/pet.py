# pet.py
import pygame
import os
import win32gui
import win32con
import win32api
class DesktopPet:
    def __init__(self):
        pygame.init()
        # 加载宠物图片
        self.image = pygame.image.load(os.path.join("assets", "pet", "pic", "pet_test.png"))
        self.rect = self.image.get_rect()
        
        # 创建透明窗口
        self.screen = pygame.display.set_mode((self.rect.width, self.rect.height), pygame.NOFRAME)
        pygame.display.set_caption("Desktop Pet")
        
        # 设置窗口透明
        self.transparent()
        hwnd = pygame.display.get_wm_info()["window"]
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED)

        win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 0, win32con.LWA_COLORKEY)
    # 设置透明(不知道为什么没用)
    def transparent(self):
        transparent = (0, 0, 0, 0)
        self.screen.fill(transparent)
    
    def update(self):
        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()

def pet_run():
    pet = DesktopPet()
        
    running = True
    pet.__init__()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pet.update()
