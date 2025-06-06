from src.entity.pet_status import PetStatus
from src.entity.menu import get_menu_items, get_status_menu_items
from src.utils.load_images_from_folder import load_images_from_folder
from src.utils.contextmenu import ContextMenu
from src.utils.state_manager import StateManager
from src.utils.animation import Animation
from src.utils.window_manager import WindowManager

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

        hwnd = pygame.display.get_wm_info()["window"]
        WindowManager.set_transparent(hwnd)
        WindowManager.set_topmost(hwnd)
        
    def update(self):
        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()
        

def pet_run():
    pet = DesktopPet()
    animation = Animation(pet.screen)
    state_manager = StateManager()
    running = True

    standing_frames = load_images_from_folder(r'assets\pet\image\Standing')
    idle_frames = load_images_from_folder(r'assets\pet\image\Idle')

    frame_index = 0
    clock = pygame.time.Clock()

    is_topmost = True
    context_menu = None
    status_menu = None

    while running:
        for event in pygame.event.get():
            # 右键菜单显示/隐藏
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()

                # 根據當前狀態選擇正確的帧序列
                if pet.status == PetStatus.STANDING:
                    frames = standing_frames
                elif pet.status == PetStatus.IDLE:
                    frames = idle_frames
                else:
                    frames = []  # 如果有其他狀態，需處理對應的帧序列

                # 确保 frame_index 不超出范围
                if frames:
                    frame = frames[frame_index % len(frames)]
                    img_x = pet.screen.get_width() // 2 - frame.get_width() // 2
                    img_y = pet.screen.get_height() // 2 - frame.get_height() // 2
                    img_rect = pygame.Rect(img_x, img_y, frame.get_width(), frame.get_height())
                    if img_rect.collidepoint(mouse_pos):
                        if context_menu and context_menu.visible:
                            context_menu.visible = False
                        else:
                            context_menu = ContextMenu(pet.screen, get_menu_items(is_topmost), mouse_pos)
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
                    state_manager.set_status(PetStatus.STANDING)  # 更新状态
                    state_manager.reset_idle_timer()  # 重置定时器
                    frame_index = 0
                    status_menu = None
                    context_menu = None
                elif result == 'set_idle':
                    state_manager.set_status(PetStatus.IDLE)  # 更新状态
                    state_manager.reset_idle_timer()  # 重置定时器
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
        pet.status = state_manager.update_status()

        # 根据状态选择帧序列
        if pet.status == PetStatus.STANDING:
            frames = standing_frames
        elif pet.status == PetStatus.IDLE:
            frames = idle_frames
        else:
            # 未來可以加入其他狀態的帧序列
            frames = []

        # 播放动画
        animation.play_frame(frames, frame_index)

        # 更新帧索引
        if pet.status != PetStatus.STANDING:  # 非 STANDING 狀態
            frame_index += 1
            if frame_index >= len(frames):  # 如果當前狀態的動畫播放完一輪
                state_manager.status_complete = True  # 標記為完成
                frame_index = 0  # 重置帧索引
        else:
            frame_index = (frame_index + 1) % len(frames)  # 循環播放 STANDING 動畫

        # 繪製菜單（保持原樣）
        if context_menu and context_menu.visible:
            context_menu.draw()
        if status_menu and status_menu.visible:
            status_menu.draw()

        pygame.display.flip()
        clock.tick(6)
