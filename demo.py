import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置窗口
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame 测试 Demo")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 矩形初始位置和大小
rect_x, rect_y = width // 2, height // 2
rect_width, rect_height = 50, 50
rect_speed = 5

# 游戏主循环
clock = pygame.time.Clock()
running = True

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            print(f"按下了键: {pygame.key.name(event.key)}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"鼠标点击位置: {event.pos}")

    # 获取键盘状态实现持续移动
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rect_x -= rect_speed
    if keys[pygame.K_RIGHT]:
        rect_x += rect_speed
    if keys[pygame.K_UP]:
        rect_y -= rect_speed
    if keys[pygame.K_DOWN]:
        rect_y += rect_speed

    # 确保矩形不会移出屏幕
    rect_x = max(0, min(rect_x, width - rect_width))
    rect_y = max(0, min(rect_y, height - rect_height))

    # 绘制
    screen.fill(WHITE)  # 填充白色背景
    
    # 绘制矩形
    pygame.draw.rect(screen, RED, (rect_x, rect_y, rect_width, rect_height))
    
    # 获取鼠标位置并绘制一个小蓝点
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, BLUE, (mouse_x, mouse_y), 10)

    # 更新显示
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)

# 退出 Pygame
pygame.quit()
sys.exit()