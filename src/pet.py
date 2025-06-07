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
import win32api 


class DesktopPet:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Desktop Pet")
        self.screen = pygame.display.set_mode((500, 500), pygame.NOFRAME | pygame.SRCALPHA)
        hwnd = pygame.display.get_wm_info()["window"]
        WindowManager.set_transparent(hwnd)
        WindowManager.set_topmost(hwnd)
        WindowManager.set_always_interactive(hwnd)  # 设置窗口始终可交互
        self.status = PetStatus.STANDING
        self.is_dragging = False
        self.drag_offset = (0, 0)

    def update(self):
        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()


def pet_run():
    pet = DesktopPet()
    hwnd = pygame.display.get_wm_info()["window"]
    animation = Animation(pet.screen)
    state_manager = StateManager()
    running = True
    path = r'assets\pet\image'
    standing_frames = load_images_from_folder(os.path.join(path, PetStatus.STANDING.value))
    idle_frames = load_images_from_folder(os.path.join(path, PetStatus.IDLE.value))
    dragging_frames = load_images_from_folder(os.path.join(path, PetStatus.DRAGGING.value))
    touching_head_frames = load_images_from_folder(os.path.join(path, PetStatus.TOUCHING_HEAD.value))
    touching_body_frames = load_images_from_folder(os.path.join(path, PetStatus.TOUCHING_BODY.value))
    frame_index = 0
    clock = pygame.time.Clock()

    # 帧率设置
    high_fps = 30
    normal_fps = 6

    is_topmost = True
    context_menu = None
    status_menu = None

    # 偏移量变量
    offset_x = 0
    offset_y = 0
    while running:
        # 检查是否应该开始拖拽 - 新增的直接状态检测
        if state_manager.status != PetStatus.DRAGGING:
            # 直接检测鼠标中键状态（不依赖pygame事件）
            middle_button_state = win32api.GetKeyState(0x04)  # 0x04是鼠标中键
            if middle_button_state < 0:  # 按钮已按下
                # 获取屏幕坐标中的光标位置
                mouse_abs = win32gui.GetCursorPos()
                # 获取窗口位置
                window_pos = win32gui.GetWindowRect(hwnd)
                # 计算相对于窗口的位置
                rel_x = mouse_abs[0] - window_pos[0]
                rel_y = mouse_abs[1] - window_pos[1]
                
                # 检查光标是否在宠物上
                pet_rect = pygame.Rect(
                    pet.screen.get_width() // 2 - standing_frames[0].get_width() // 2,
                    pet.screen.get_height() // 2 - standing_frames[0].get_height() // 2,
                    standing_frames[0].get_width(),
                    standing_frames[0].get_height(),
                )
                
                if (0 <= rel_x < pet.screen.get_width() and 
                    0 <= rel_y < pet.screen.get_height() and 
                    pet_rect.collidepoint((rel_x, rel_y))):
                    
                    state_manager.set_status(PetStatus.DRAGGING)
                    pet.is_dragging = True
                    
                    # 直接计算拖拽的偏移量
                    offset_x = mouse_abs[0] - window_pos[0]
                    offset_y = mouse_abs[1] - window_pos[1]
                    
        # 拖拽状态下检测中键是否松开 - 现有代码
        if state_manager.status == PetStatus.DRAGGING:
            # 直接检测鼠标中键状态（不依赖pygame事件）
            middle_button_state = win32api.GetKeyState(0x04)  # 0x04是鼠标中键
            if middle_button_state >= 0:  # 按钮未按下
                state_manager.set_status(PetStatus.STANDING)
                pet.is_dragging = False
                
            # 直接处理鼠标位置（原有代码）
            current_screen_pos = win32gui.GetCursorPos()
            new_x = current_screen_pos[0] - offset_x
            new_y = current_screen_pos[1] - offset_y
            
            # 更新窗口位置
            win32gui.SetWindowPos(
                hwnd, None,
                new_x, new_y,
                0, 0,
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            )
        for event in pygame.event.get():
            # 右键菜单显示/隐藏
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                if context_menu and context_menu.visible:
                    context_menu.visible = False  # 隐藏菜单
                else:
                    context_menu = ContextMenu(pet.screen, get_menu_items(is_topmost), mouse_pos)  # 显示菜单
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not (context_menu and context_menu.visible):
                    mouse_pos = event.pos
                    pet_rect = pygame.Rect(
                        pet.screen.get_width() // 2 - standing_frames[0].get_width() // 2,
                        pet.screen.get_height() // 2 - standing_frames[0].get_height() // 2,
                        standing_frames[0].get_width(),
                        standing_frames[0].get_height(),
                    )
                    third_height = pet_rect.height * 0.4
                    if mouse_pos[1] < pet_rect.top + third_height:  # 点击头部区域
                        state_manager.set_status(PetStatus.TOUCHING_HEAD)
                    else:
                        state_manager.set_status(PetStatus.TOUCHING_BODY)

            # 检测鼠标拖拽事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                mouse_pos = event.pos
                pet_rect = pygame.Rect(
                    pet.screen.get_width() // 2 - standing_frames[0].get_width() // 2,
                    pet.screen.get_height() // 2 - standing_frames[0].get_height() // 2,
                    standing_frames[0].get_width(),
                    standing_frames[0].get_height(),
                )
                if pet_rect.collidepoint(mouse_pos):
                    state_manager.set_status(PetStatus.DRAGGING)
                    offset_x = mouse_pos[0]
                    offset_y = mouse_pos[1]
                    pet.is_dragging = True

                    # 更新位置
                    window_pos = win32gui.GetWindowRect(hwnd)
                    mouse_abs = win32gui.GetCursorPos()
                    offset_x = mouse_abs[0] - window_pos[0]
                    offset_y = mouse_abs[1] - window_pos[1]
            

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                if state_manager.status == PetStatus.DRAGGING:
                    state_manager.set_status(PetStatus.STANDING)
                    pet.is_dragging = False 

            elif event.type == pygame.MOUSEMOTION:
                if state_manager.status == PetStatus.DRAGGING:
                    current_screen_pos = win32gui.GetCursorPos()
                    new_x = current_screen_pos[0] - offset_x
                    new_y = current_screen_pos[1] - offset_y
                    hwnd = pygame.display.get_wm_info()["window"]
                    win32gui.SetWindowPos(
                        hwnd, None,
                        new_x, new_y,
                        0, 0,
                        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                    )
                    pet_position = [new_x, new_y]

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
                    context_menu = None
                elif result == 'switch_status_menu':
                    menu_x, menu_y = context_menu.position
                    status_menu_pos = (menu_x + context_menu.width + 10, menu_y)
                    status_menu = ContextMenu(pet.screen, get_status_menu_items(), status_menu_pos)
                continue

            # 状态菜单事件
            if status_menu and status_menu.visible:
                result = status_menu.handle_event(event)
                if result == 'set_standing':
                    state_manager.set_status(PetStatus.STANDING)
                    state_manager.reset_idle_timer()
                    frame_index = 0
                    status_menu = None
                    context_menu = None
                elif result == 'set_idle':
                    state_manager.set_status(PetStatus.IDLE)
                    state_manager.reset_idle_timer()
                    frame_index = 0
                    status_menu = None
                    context_menu = None
                continue

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 状态定时切换
        pet.status = state_manager.update_status()

        # 根据状态选择帧序列
        if pet.status == PetStatus.STANDING:
            frames = standing_frames
        elif pet.status == PetStatus.IDLE:
            frames = idle_frames
        elif pet.status == PetStatus.DRAGGING:
            frames = dragging_frames
        elif pet.status == PetStatus.TOUCHING_HEAD:
            frames = touching_head_frames
        elif pet.status == PetStatus.TOUCHING_BODY:
            frames = touching_body_frames
        else:
            frames = []

        is_dragging = state_manager.status == PetStatus.DRAGGING
        animation.play_frame(frames, frame_index, is_dragging)

        # 更新帧索引
        if pet.status in [PetStatus.STANDING, PetStatus.DRAGGING]:
            frame_index = (frame_index + 1) % len(frames)
        else:
            frame_index += 1
            if frame_index >= len(frames):
                state_manager.status_complete = True
                frame_index = 0

        # 绘制菜单
        if context_menu and context_menu.visible:
            context_menu.draw()
        if status_menu and status_menu.visible:
            status_menu.draw()

        pygame.display.flip()

        # 根据状态调整帧率
        if state_manager.status == PetStatus.DRAGGING:
            clock.tick(high_fps)
        else:
            clock.tick(normal_fps)