from src.utils.load_images_from_folder import load_images_from_folder

from src.utils.contextmenu import ContextMenu

import pygame
import os
import win32gui
import win32con
import win32api


class DesktopPet:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 1000), pygame.NOFRAME)

        pygame.init()
        
        pygame.display.set_caption("Desktop Pet")
        
        # 设置窗口透明
        self.transparent()
        # 设置窗口置顶
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    # 设置透明
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
    frames = load_images_from_folder(r'assets\image')
    frame_index = 0
    clock = pygame.time.Clock()

    is_topmost = True  # 初始为置顶

    def get_menu_items():
        return [
            {'text': '退出', 'action': 'quit'},
            {'text': '取消置顶' if is_topmost else '置顶', 'action': 'toggle_topmost'},
        ]

    context_menu = None

    while running:
        for event in pygame.event.get():
            # 右键菜单显示/隐藏
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                frame = frames[frame_index]
                img_x = pet.screen.get_width() // 2 - frame.get_width() // 2
                img_y = pet.screen.get_height() // 2 - frame.get_height() // 2
                img_rect = pygame.Rect(img_x, img_y, frame.get_width(), frame.get_height())
                if img_rect.collidepoint(mouse_pos):
                    if context_menu and context_menu.visible:
                        context_menu.visible = False
                    else:
                        context_menu = ContextMenu(pet.screen, get_menu_items(), mouse_pos)
                continue

            # 菜单事件
            if context_menu and context_menu.visible:
                result = context_menu.handle_event(event)
                if result == 'quit':
                    running = False
                elif result == 'toggle_topmost':
                    hwnd = pygame.display.get_wm_info()["window"]
                    if is_topmost:
                        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        is_topmost = False
                    else:
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        is_topmost = True
                    # 更新菜单显示
                    context_menu = None
                continue

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pet.screen.fill((0, 0, 0))
        frame = frames[frame_index]
        pet.screen.blit(frame, (pet.screen.get_width() // 2 - frame.get_width() // 2,
                                pet.screen.get_height() // 2 - frame.get_height() // 2))
        frame_index = (frame_index + 1) % len(frames)

        if context_menu and context_menu.visible:
            context_menu.draw()

        pygame.display.flip()
        clock.tick(6)  # 每秒播放 6 帧
