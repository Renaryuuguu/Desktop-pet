import random
import pygame
from src.entity.pet_status import PetStatus

class StateManager:
    def __init__(self):
        self.status = PetStatus.STANDING
        self.next_idle_time = pygame.time.get_ticks() + random.randint(3000, 5000)  # 3-5秒後切換狀態
        self.status_complete = False  # 用於追蹤當前狀態是否完成

    def update_status(self):
        now = pygame.time.get_ticks()
        if self.status == PetStatus.STANDING and now >= self.next_idle_time:
            self.status = PetStatus.IDLE
            self.status_complete = False  # 重置為未完成
            self.next_idle_time = None  # 清除定時器
        elif self.status != PetStatus.STANDING and self.status_complete:
            # 當非 STANDING 狀態完成後切換回 STANDING
            self.status = PetStatus.STANDING
            self.reset_idle_timer()  # 重置定時器
        return self.status

    def reset_idle_timer(self):
        self.next_idle_time = pygame.time.get_ticks() + random.randint(3000, 5000)

    def set_status(self, new_status):
        self.status = new_status
        self.status_complete = False  # 重置為未完成