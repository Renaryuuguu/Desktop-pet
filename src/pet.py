from src.entity.pet_status import PetStatus
from src.entity.menu import get_menu_items, get_status_menu_items
from src.utils.load_images_from_folder import load_images_from_folder
from src.utils.contextmenu import ContextMenu
from src.utils.state_manager import StateManager
from src.utils.animation import Animation
from src.utils.window_manager import WindowManager
import pygame
import os
import threading
import win32api
import win32con
import win32gui
import time

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

    def start_middle_button_listener(self):
        def listener():
            prev_state = win32api.GetKeyState(0x04)  # 中键状态
            while self.running:
                current_state = win32api.GetKeyState(0x04)
                # 检测中键按下事件
                if current_state != prev_state:
                    if current_state < 0:  # 中键按下
                        self.middle_button_pressed.set()
                    else:  # 中键释放
                        self.middle_button_released.set()
                    prev_state = current_state
                time.sleep(0.01)  # 10毫秒检测间隔
        threading.Thread(target=listener, daemon=True).start()

def get_pet_rect(screen, frame):
    return pygame.Rect(
        screen.get_width() // 2 - frame.get_width() // 2,
        screen.get_height() // 2 - frame.get_height() // 2,
        frame.get_width(),
        frame.get_height(),
    )

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
    enter_sleeping_frames = load_images_from_folder(os.path.join(path, PetStatus.SLEEPING.value, "Enter_Sleeping"))
    sleeping_frames = load_images_from_folder(os.path.join(path, PetStatus.SLEEPING.value, "Sleeping"))
    leave_sleeping_frames = load_images_from_folder(os.path.join(path, PetStatus.SLEEPING.value, "Leave_Sleeping"))
    frame_index = 0
    clock = pygame.time.Clock()
    # 监听中键
    pet.middle_button_pressed = threading.Event()
    pet.middle_button_released = threading.Event()
    pet.running = True
    pet.start_middle_button_listener()

    # 帧率设置
    high_fps = 45
    normal_fps = 6

    is_topmost = True
    context_menu = None
    status_menu = None

    # 拖拽状态变量
    is_dragging = False
    drag_offset_x = 0
    drag_offset_y = 0
    
    try:
        while running:
            # 处理中键按下事件
            if pet.middle_button_pressed.is_set():
                pet.middle_button_pressed.clear()
                # 获取鼠标位置和窗口位置
                mouse_abs = win32gui.GetCursorPos()
                window_pos = win32gui.GetWindowRect(hwnd)
                
                # 计算相对位置
                rel_x = mouse_abs[0] - window_pos[0]
                rel_y = mouse_abs[1] - window_pos[1]
                
                # 检查是否在宠物上
                pet_rect = get_pet_rect(pet.screen, standing_frames[0])
                if pet_rect.collidepoint((rel_x, rel_y)):
                    is_dragging = True
                    state_manager.set_status(PetStatus.DRAGGING)
                    drag_offset_x = rel_x
                    drag_offset_y = rel_y
                    
                    # 切换到高帧率确保拖拽流畅
                    clock = pygame.time.Clock()
                    clock.tick(30)
            
            # 处理中键释放事件
            if pet.middle_button_released.is_set():
                pet.middle_button_released.clear()
                if is_dragging:
                    is_dragging = False
                    state_manager.set_status(PetStatus.STANDING)
            
            # 处理拖拽移动
            if is_dragging:
                current_pos = win32gui.GetCursorPos()
                new_x = current_pos[0] - drag_offset_x
                new_y = current_pos[1] - drag_offset_y
                win32gui.SetWindowPos(
                    hwnd, None,
                    new_x, new_y,
                    0, 0,
                    win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                )
            # 事件处理
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
                        pet_rect = get_pet_rect(pet.screen, standing_frames[0])
                        third_height = pet_rect.height * 0.4
                        if mouse_pos[1] < pet_rect.top + third_height:  # 点击头部区域
                            state_manager.set_status(PetStatus.TOUCHING_HEAD)
                            frame_index = 0
                        else:
                            state_manager.set_status(PetStatus.TOUCHING_BODY)
                            frame_index = 0

                # 主菜单事件
                if context_menu and context_menu.visible:
                    result = context_menu.handle_event(event)
                    if result == 'quit':
                        running = False
                        status_menu = None
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
                        status_menu = None 
                    elif result == 'switch_status_menu':
                        menu_x, menu_y = context_menu.position
                        status_menu_pos = (menu_x + context_menu.width + 10, menu_y)
                        status_menu = ContextMenu(pet.screen, get_status_menu_items(), status_menu_pos)
                        context_menu.visible = True  # 保持主菜单可见

                # 状态菜单事件
                if status_menu and status_menu.visible:
                    result = status_menu.handle_event(event)
                    if result == 'set_standing':
                        state_manager.set_status(PetStatus.STANDING)
                        frame_index = 0
                        status_menu = None
                        context_menu = None
                    elif result == 'set_idle':
                        state_manager.set_status(PetStatus.IDLE)
                        frame_index = 0
                        status_menu = None
                        context_menu = None
                    elif result == 'set_sleeping':
                        state_manager.set_status(PetStatus.SLEEPING, sub_status="enter")
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
            elif pet.status == PetStatus.SLEEPING:
                if state_manager.sub_status == "enter":
                    frames = enter_sleeping_frames
                elif state_manager.sub_status == "loop":
                    frames = sleeping_frames
                elif state_manager.sub_status == "leave":
                    frames = leave_sleeping_frames
                else:
                    state_manager.sub_status = "enter"
                    frame_index = 0
            else:
                frames = []

            animation.play_frame(frames, frame_index, is_dragging)

            # 更新帧索引
            if pet.status == PetStatus.SLEEPING:
                if state_manager.sub_status == "enter" and frame_index >= len(enter_sleeping_frames) - 1:
                    state_manager.sub_status = "loop"
                    frame_index = 0
                elif state_manager.sub_status == "leave" and frame_index >= len(leave_sleeping_frames) - 1:
                    state_manager.status_complete = True
                    frame_index = 0
                elif frame_index < len(frames) - 1:
                    frame_index += 1
                elif state_manager.sub_status == "loop":
                    frame_index = 0
            elif pet.status in [PetStatus.STANDING, PetStatus.DRAGGING]:
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
            if state_manager.status == PetStatus.DRAGGING and PetStatus.STANDING:
                clock.tick(high_fps)
            else:
                clock.tick(normal_fps)
    finally:
        pet.running = False  # 停止监听线程