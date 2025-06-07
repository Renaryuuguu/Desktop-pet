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
        
        pygame.init()
        pygame.display.set_caption("Desktop Pet")
        # self.screen = pygame.display.set_mode((1000, 1000), pygame.NOFRAME | pygame.SRCALPHA)
        self.screen = pygame.display.set_mode((500, 500))
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
    path = r'assets\pet\image'
    standing_frames = load_images_from_folder(os.path.join(path, PetStatus.STANDING.value))
    idle_frames = load_images_from_folder(os.path.join(path, PetStatus.IDLE.value))
    dragging_frames = load_images_from_folder(os.path.join(path, PetStatus.DRAGGING.value))  # 加载 DRAGGING 动画帧
    touching_head_frames = load_images_from_folder(os.path.join(path, PetStatus.TOUCHING_HEAD.value))  # 加载 TOUCHES 动画帧
    touching_body_frames = load_images_from_folder(os.path.join(path, PetStatus.TOUCHING_BODY.value))  # 加载 TOUCHES 动画帧
    # print(os.path.join(path, 'preview.png'))
    frame_index = 0
    clock = pygame.time.Clock()

    # 帧率设置
    high_fps = 30  # 拖拽时的高帧率
    normal_fps = 6   # 正常帧率

    is_topmost = True
    context_menu = None
    status_menu = None

    # 添加偏移量变量
    offset_x = 0
    offset_y = 0
    while running:
        for event in pygame.event.get():
            # 右键菜单显示/隐藏
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 右鍵按下
                mouse_pos = pygame.mouse.get_pos()
                if context_menu and context_menu.visible:
                    context_menu.visible = False  # 如果菜單已顯示，則隱藏
                else:
                    context_menu = ContextMenu(pet.screen, get_menu_items(is_topmost), mouse_pos)  # 顯示菜單
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左鍵按下
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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # 中键按下
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
                    # 记录鼠标在窗口内的位置（相对于窗口左上角）
                    offset_x = mouse_pos[0]
                    offset_y = mouse_pos[1]
                    
                    # 立即更新一次位置，避免初始延迟
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

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:  # 中键释放
                # 如果当前状态是拖拽，则结束拖拽
                if state_manager.status == PetStatus.DRAGGING:
                    state_manager.set_status(PetStatus.STANDING)

            elif event.type == pygame.MOUSEMOTION:
                # 如果当前状态是拖拽，则移动窗口
                if state_manager.status == PetStatus.DRAGGING:
                    # 获取当前鼠标的屏幕坐标
                    current_screen_pos = win32gui.GetCursorPos()
                    
                    # 计算新的窗口位置（直接使用鼠标屏幕坐标减去偏移量）
                    new_x = current_screen_pos[0] - offset_x
                    new_y = current_screen_pos[1] - offset_y
                    
                    # 移动窗口
                    hwnd = pygame.display.get_wm_info()["window"]
                    win32gui.SetWindowPos(
                        hwnd, None, 
                        new_x, new_y, 
                        0, 0, 
                        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
                    )
                    # 更新宠物位置
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
        # 如果主菜单显示，检测鼠标是否悬停在"切换状态"项
        if context_menu and context_menu.visible:
            # 找到"切换状态"项的rect
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
        elif pet.status == PetStatus.TOUCHING_HEAD:
            frames = touching_head_frames 
        elif pet.status == PetStatus.TOUCHING_BODY:
            frames = touching_body_frames
        else:
            frames = []  # 如果有其他狀態，需處理對應的幀序列


        is_dragging = state_manager.status == PetStatus.DRAGGING
        # 播放動畫
        animation.play_frame(frames, frame_index, is_dragging)

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
        
        # 根据状态调整帧率
        if state_manager.status == PetStatus.DRAGGING:
            clock.tick(high_fps)
        else:
            clock.tick(normal_fps)