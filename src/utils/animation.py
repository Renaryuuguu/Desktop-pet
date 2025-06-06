import pygame

class Animation:
    def __init__(self, screen):
        self.screen = screen

    def play_frame(self, frames, frame_index):
        frame = frames[frame_index % len(frames)]
        self.screen.fill((0, 0, 0))
        self.screen.blit(
            frame,
            (self.screen.get_width() // 2 - frame.get_width() // 2,
             self.screen.get_height() // 2 - frame.get_height() // 2)
        )
        return frame