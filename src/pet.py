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
import random


class DesktopPet:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 1000), pygame.NOFRAME)
        pygame.init()
        pygame.display.set_caption("Desktop Pet")

        hwnd = pygame.display.get_wm_info()["window"]
        WindowManager.set_transparent(hwnd)
        WindowManager.set_topmost(hwnd)
        self.status = PetStatus.STANDING
        
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
    dragging_frames = load_images_from_folder(r'assets\pet\image\Dragging')  # 加载 DRAGGING 动画帧

    frame_index = 0
    clock = pygame.time.Clock()

    is_topmost = True
    context_menu = None
    status_menu = None

    # 添加偏移量变量
    offset_x = 0
    offset_y = 0
    dragging = False

    while running:
        for event in pygame.event.get():
            # 右键菜单显示/隐藏
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 右鍵按下
                mouse_pos = pygame.mouse.get_pos()
                if context_menu and context_menu.visible:
                    context_menu.visible = False  # 如果菜單已顯示，則隱藏
                else:
                    context_menu = ContextMenu(pet.screen, get_menu_items(is_topmost), mouse_pos)  # 顯示菜單

            # 检测鼠标拖拽事件
            # 在 MOUSEBUTTONDOWN 中记录偏移量
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键按下
                mouse_pos = event.pos
                # 计算宠物图片的位置
                pet_rect = pygame.Rect(
                    pet.screen.get_width() // 2 - standing_frames[0].get_width() // 2,
                    pet.screen.get_height() // 2 - standing_frames[0].get_height() // 2,
                    standing_frames[0].get_width(),
                    standing_frames[0].get_height(),
                )
                
                if pet_rect.collidepoint(mouse_pos):
                    state_manager.set_status(PetStatus.DRAGGING)
                    dragging = True  # 设置拖拽标志
                    
                    # 获取窗口当前位置
                    hwnd = pygame.display.get_wm_info()["window"]
                    window_rect = win32gui.GetWindowRect(hwnd)
                    
                    # 计算鼠标在窗口内的位置
                    offset_x = mouse_pos[0]
                    offset_y = mouse_pos[1]

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # 左键释放
                if dragging:  # 确保只处理拖拽结束
                    state_manager.set_status(PetStatus.STANDING)
                    dragging = False  # 清除拖拽标志

            elif event.type == pygame.MOUSEMOTION and dragging:  # 拖拽中
                mouse_pos = event.pos
                hwnd = pygame.display.get_wm_info()["window"]
                
                # 获取当前鼠标的屏幕坐标
                current_screen_pos = win32gui.GetCursorPos()
                
                # 计算新的窗口位置（直接使用鼠标屏幕坐标减去偏移量）
                new_x = current_screen_pos[0] - offset_x
                new_y = current_screen_pos[1] - offset_y
                
                # 移动窗口
                win32gui.SetWindowPos(
                    hwnd, None, 
                    new_x, new_y, 
                    0, 0, 
                    win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                )
                # 更新宠物位置
                pet_position = [new_x, new_y]
                continue  # 跳过后续事件处理

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
        elif pet.status == PetStatus.DRAGGING:
            frames = dragging_frames  # 循環播放 DRAGGING 動畫
        else:
            frames = []  # 如果有其他狀態，需處理對應的幀序列

        # 播放動畫
        animation.play_frame(frames, frame_index)

        # 更新帧索引
        if pet.status in [PetStatus.STANDING, PetStatus.DRAGGING]:  # 循環播放 STANDING 和 DRAGGING 動畫
            frame_index = (frame_index + 1) % len(frames)
        else:
            frame_index += 1
            if frame_index >= len(frames):  # 如果當前狀態的動畫播放完一輪
                state_manager.status_complete = True  # 標記為完成
                frame_index = 0  # 重置幀索引

        # 繪製菜單（保持原樣）
        if context_menu and context_menu.visible:
            context_menu.draw()
        if status_menu and status_menu.visible:
            status_menu.draw()

        pygame.display.flip()
        clock.tick(6)
