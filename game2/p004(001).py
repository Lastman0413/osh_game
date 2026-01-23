

import pygame
import math

# --- 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상
COLOR_TILE = (120, 120, 120)
COLOR_PLAYER = (0, 0, 0)
WHITE = (255, 255, 255)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(0, 0)
        self.speed = 5
        self.walk_count = 0
        
        # 신체 규격
        self.head_r = 12
        self.body_w, self.body_h = 22, 35
        self.limb_len = 25 # 팔다리 길이
        self.line_thickness = 3 # 선의 굵기

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        
        # 조작 보정
        if keys[pygame.K_w]: move.y -= 1; move.x -= 1
        if keys[pygame.K_s]: move.y += 1; move.x += 1
        if keys[pygame.K_a]: move.x -= 1; move.y += 1
        if keys[pygame.K_d]: move.x += 1; move.y -= 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            self.world_pos += move
            self.walk_count += 0.15
        else:
            self.walk_count = 0

    def draw(self, surface):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # 애니메이션 계산 (각도나 변위로 활용)
        swing = math.sin(self.walk_count) * 12
        
        # 1. 다리 (선으로 구현)
        # 왼쪽 다리: 몸통 하단 왼쪽에서 시작
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 6, cy + 5), (cx - 6 - swing/2, cy + 5 + self.limb_len + swing), self.line_thickness)
        # 오른쪽 다리: 몸통 하단 오른쪽에서 시작
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 6, cy + 5), (cx + 6 + swing/2, cy + 5 + self.limb_len - swing), self.line_thickness)

        # 2. 몸통 (중심 사각형)
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 30, self.body_w, self.body_h), 2)

        # 3. 팔 (선으로 구현)
        # 왼쪽 팔: 몸통 상단 왼쪽에서 시작 (다리와 반대로 스윙)
        pygame.draw.line(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 25), (cx - self.body_w//2 - 10, cy - 25 + self.limb_len - swing), self.line_thickness)
        # 오른쪽 팔: 몸통 상단 오른쪽에서 시작
        pygame.draw.line(surface, COLOR_PLAYER, (cx + self.body_w//2, cy - 25), (cx + self.body_w//2 + 10, cy - 25 + self.limb_len + swing), self.line_thickness)

        # 4. 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, cy - 42), self.head_r, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    player = Player()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        player.update()
        screen.fill(WHITE)
        
        # 카메라 오프셋
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        off_x, off_y = SCREEN_WIDTH // 2 - cam_x, SCREEN_HEIGHT // 2 - cam_y

        # 타일 렌더링
        t_size = 60
        for x in range(-900, 900, t_size):
            for y in range(-900, 900, t_size):
                pts = [iso_projection(x+dx, y+dy) for dx, dy in [(0,0), (t_size,0), (t_size,t_size), (0,t_size)]]
                render_pts = [(p[0] + off_x, p[1] + off_y) for p in pts]
                
                # 컬링 (화면 안쪽만)
                if -100 < render_pts[0][0] < SCREEN_WIDTH + 100 and -100 < render_pts[0][1] < SCREEN_HEIGHT + 100:
                    pygame.draw.polygon(screen, COLOR_TILE, render_pts, 1)

        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()