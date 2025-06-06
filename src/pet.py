from src.utils.load_images_from_folder import load_images_from_folder
from src.entity.pet_status import PetStatus
from src.utils.contextmenu import ContextMenu

import pygame
import os
import win32gui
import win32con
import win32api
import random


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

    # 分别加载两种状态的帧
    standing_frames = load_images_from_folder(r'assets\pet\image\Standing')
    idle_frames = load_images_from_folder(r'assets\pet\image\Idle')

    frame_index = 0
    clock = pygame.time.Clock()

    # 状态切换相关
    pet.status = PetStatus.STANDING
    next_idle_time = pygame.time.get_ticks() + random.randint(30000, 50000)  # 30-50秒后切idle

    is_topmost = True  # 初始为置顶

    def get_menu_items():
        return [
            {'text': '退出', 'action': 'quit'},
            {'text': '取消置顶' if is_topmost else '置顶', 'action': 'toggle_topmost'},
            {'text': '切换状态', 'action': 'switch_status_menu'},
        ]
    def get_status_menu_items():
        return [
            {'text': '站立', 'action': 'set_standing'},
            {'text': '闲置', 'action': 'set_idle'},
        ]
    context_menu = None
    status_menu = None

    while running:
        for event in pygame.event.get():
            # 右键菜单显示/隐藏
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                frame = standing_frames[frame_index]
                img_x = pet.screen.get_width() // 2 - frame.get_width() // 2
                img_y = pet.screen.get_height() // 2 - frame.get_height() // 2
                img_rect = pygame.Rect(img_x, img_y, frame.get_width(), frame.get_height())
                if img_rect.collidepoint(mouse_pos):
                    if context_menu and context_menu.visible:
                        context_menu.visible = False
                    else:
                        context_menu = ContextMenu(pet.screen, get_menu_items(), mouse_pos)
                continue

            # 主菜单事件
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
                elif result == 'switch_status_menu':
                    # 弹出状态菜单，位置在主菜单右侧
                    menu_x, menu_y = context_menu.position
                    status_menu_pos = (menu_x + context_menu.width + 10, menu_y)
                    status_menu = ContextMenu(pet.screen, get_status_menu_items(), status_menu_pos)
                continue

            # 状态菜单事件
            if status_menu and status_menu.visible:
                result = status_menu.handle_event(event)
                if result == 'set_standing':
                    pet.status = PetStatus.STANDING
                    frame_index = 0
                    status_menu = None
                    context_menu = None
                elif result == 'set_idle':
                    pet.status = PetStatus.IDLE
                    frame_index = 0
                    status_menu = None
                    context_menu = None
                continue

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ----------- 悬停检测逻辑 -----------
        # 如果主菜单显示，检测鼠标是否悬停在“切换状态”项
        if context_menu and context_menu.visible:
            # 找到“切换状态”项的rect
            switch_index = None
            for idx, item in enumerate(context_menu.items):
                if item['action'] == 'switch_status_menu':
                    switch_index = idx
                    break
            if switch_index is not None:
                menu_x, menu_y = context_menu.position
                item_rect = pygame.Rect(menu_x, menu_y + switch_index * context_menu.item_height,
                                       context_menu.width, context_menu.item_height)
                if item_rect.collidepoint(mouse_pos):
                    # 悬停时弹出状态菜单
                    if not (status_menu and status_menu.visible):
                        status_menu_pos = (menu_x + context_menu.width + 10, menu_y + switch_index * context_menu.item_height)
                        status_menu = ContextMenu(pet.screen, get_status_menu_items(), status_menu_pos)
                else:
                    # 鼠标移开则关闭状态菜单
                    if status_menu and status_menu.visible:
                        status_menu.visible = False

        # 状态定时切换
        now = pygame.time.get_ticks()
        if pet.status == PetStatus.STANDING and now >= next_idle_time:
            pet.status = PetStatus.IDLE
            frame_index = 0  # 切换到idle时从第一帧开始

        # 根据状态选择帧序列
        if pet.status == PetStatus.STANDING:
            frames = standing_frames
        else:
            frames = idle_frames

        # 播放动画
        pet.screen.fill((0, 0, 0))
        frame = frames[frame_index % len(frames)]
        pet.screen.blit(frame, (pet.screen.get_width() // 2 - frame.get_width() // 2,
                                pet.screen.get_height() // 2 - frame.get_height() // 2))

        # 检查idle动画是否播放完一轮
        if pet.status == PetStatus.IDLE:
            frame_index += 1
            if frame_index >= len(idle_frames):
                pet.status = PetStatus.STANDING
                frame_index = 0
                next_idle_time = pygame.time.get_ticks() + random.randint(30000, 50000)
        else:
            frame_index = (frame_index + 1) % len(frames)

        if context_menu and context_menu.visible:
            context_menu.draw()
        if status_menu and status_menu.visible:
            status_menu.draw()

        pygame.display.flip()
        clock.tick(6)
