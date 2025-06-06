# pet.py
import pygame
import os

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
