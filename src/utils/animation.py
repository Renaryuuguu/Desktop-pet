import pygame

class Animation:
    def __init__(self, screen):
        self.screen = screen
    
    def get_pet_outline(self, image):
        """获取宠物轮廓的 mask"""
        # 创建 mask 用于检测非透明像素
        mask = pygame.mask.from_surface(image)
        # 获取 mask 的轮廓点
        outline = mask.outline()
        
        # 如果没有轮廓点，返回空列表
        if not outline:
            return []
        
        # 创建封闭的轮廓（添加第一个点作为结束点）
        return outline + [outline[0]]
    
    def draw_outline(self, image, position):
        """绘制宠物轮廓"""
        # 获取轮廓点
        outline_points = self.get_pet_outline(image)
        if not outline_points:
            return
        
        # 计算轮廓在屏幕上的位置
        screen_points = [(position[0] + x, position[1] + y) for x, y in outline_points]
        
        # 绘制轮廓
        pygame.draw.lines(self.screen, (255, 255, 0, 180), False, screen_points, 2)
    
    def play_frame(self, frames, frame_index, is_dragging=False):
        frame = frames[frame_index % len(frames)]
        self.screen.fill((0, 0, 0, 0))  # 透明背景
        
        # 计算图像位置
        x = self.screen.get_width() // 2 - frame.get_width() // 2
        y = self.screen.get_height() // 2 - frame.get_height() // 2
        
        # 绘制图像
        self.screen.blit(frame, (x, y))
        
        # 如果处于拖拽状态，绘制宠物轮廓
        if is_dragging:
            self.draw_outline(frame, (x, y))
        
        return frame