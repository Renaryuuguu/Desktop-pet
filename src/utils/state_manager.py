import random
import pygame
from src.entity.pet_status import PetStatus

class StateManager:
    def __init__(self):
        self.status = PetStatus.STANDING
        self.sub_status = None  # 子状态
        self.next_idle_time = pygame.time.get_ticks() + random.randint(3000, 5000)
        self.status_complete = False
        self.pending_status = None  # 用于存储目标状态

    def set_status(self, new_status, sub_status=None):
        if self.status == PetStatus.SLEEPING and new_status != PetStatus.DRAGGING:
            # 如果当前状态是睡觉，且目标状态不是拖拽，先播放离开睡觉动画
            self.pending_status = new_status
            self.status = PetStatus.SLEEPING
            self.sub_status = "leave"
        else:
            # 正常切换状态
            self.status = new_status
            self.sub_status = sub_status
            self.status_complete = False
            self.reset_idle_timer()

    def update_status(self):
        now = pygame.time.get_ticks()
        if self.status == PetStatus.SLEEPING and self.sub_status == "leave" and self.status_complete:
            # 离开睡觉动画播放完成后切换到目标状态
            self.status = self.pending_status
            self.sub_status = None
            self.pending_status = None
            self.status_complete = False
        elif self.status == PetStatus.STANDING and self.next_idle_time is not None and now >= self.next_idle_time:
            self.status = PetStatus.IDLE
            self.status_complete = False
            self.next_idle_time = None
        elif self.status != PetStatus.STANDING and self.status_complete:
            self.status = PetStatus.STANDING
            self.reset_idle_timer()
        return self.status

    def reset_idle_timer(self):
        self.next_idle_time = pygame.time.get_ticks() + random.randint(3000, 5000)