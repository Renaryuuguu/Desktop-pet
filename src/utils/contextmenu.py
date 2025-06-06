import pygame

class ContextMenu:
    def __init__(self, screen, items, position):
        self.screen = screen
        self.items = items
        self.position = position
        self.font = pygame.font.SysFont('SimHei', 24)  # 使用支持中文的字体
        self.visible = True
        
        # 计算菜单大小
        max_width = 0
        for item in items:
            text_width, _ = self.font.size(item['text'])
            if text_width > max_width:
                max_width = text_width
                
        self.item_height = 30
        self.width = max_width + 20
        self.height = len(items) * self.item_height
        
        # 创建菜单表面（带透明度）
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((40, 40, 40, 200))  # 半透明灰色背景
        
        # 绘制菜单项
        for i, item in enumerate(items):
            text_surface = self.font.render(item['text'], True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(10, i * self.item_height + 5))
            self.surface.blit(text_surface, text_rect)
            
            # 绘制分隔线
            if i < len(items) - 1:
                pygame.draw.line(
                    self.surface, 
                    (100, 100, 100, 150), 
                    (0, (i + 1) * self.item_height), 
                    (self.width, (i + 1) * self.item_height), 
                    1
                )
    
    def draw(self):
        if self.visible:
            # 确保菜单位置不会超出屏幕
            screen_width, screen_height = self.screen.get_size()
            x, y = self.position
            
            if x + self.width > screen_width:
                x = screen_width - self.width
            if y + self.height > screen_height:
                y = screen_height - self.height
                
            self.screen.blit(self.surface, (x, y))
    
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            menu_x, menu_y = self.position
            
            # 检查点击是否在菜单内
            if (menu_x <= mouse_pos[0] <= menu_x + self.width and 
                menu_y <= mouse_pos[1] <= menu_y + self.height):
                
                # 确定点击了哪个菜单项
                relative_y = mouse_pos[1] - menu_y
                item_index = relative_y // self.item_height
                
                if 0 <= item_index < len(self.items):
                    self.visible = False
                    return self.items[item_index]['action']
        
        return False