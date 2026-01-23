

import pygame
import math

# --- 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

TILE_SIZE = 60
MAP_TILES = 10 
MAP_LIMIT = TILE_SIZE * MAP_TILES

COLOR_BG = (255, 255, 255)
COLOR_TILE = (180, 180, 180)
COLOR_BORDER = (255, 100, 100) # 경계선 색상
COLOR_PLAYER = (0, 0, 0)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        # 정확히 맵 중앙에서 시작
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.speed = 5
        self.walk_count = 0
        
        self.head_r = 12
        self.body_w, self.body_h = 22, 35
        self.limb_len = 25
        self.line_thickness = 3

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w]: move.y -= 1; move.x -= 1
        if keys[pygame.K_s]: move.y += 1; move.x += 1
        if keys[pygame.K_a]: move.x -= 1; move.y += 1
        if keys[pygame.K_d]: move.x += 1; move.y -= 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            next_pos = self.world_pos + move
            
            # 정확한 경계 클램핑 (0.0 ~ MAP_LIMIT)
            self.world_pos.x = max(0, min(next_pos.x, MAP_LIMIT))
            self.world_pos.y = max(0, min(next_pos.y, MAP_LIMIT))
            self.walk_count += 0.15
        else:
            self.walk_count = 0

    def draw(self, surface):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 12
        
        # 발바닥(cy)이 기준점이 되도록 모든 부위의 y좌표를 위로 올림
        # 다리
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 6, cy), 
                         (cx - 6 - swing/2, cy + self.limb_len + swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 6, cy), 
                         (cx + 6 + swing/2, cy + self.limb_len - swing), self.line_thickness)
        # 몸통
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 35, self.body_w, self.body_h), 2)
        # 팔
        pygame.draw.line(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 30), 
                         (cx - self.body_w//2 - 10, cy - 30 + self.limb_len - swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + self.body_w//2, cy - 30), 
                         (cx + self.body_w//2 + 10, cy - 30 + self.limb_len + swing), self.line_thickness)
        # 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, cy - 47), self.head_r, 2)

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
        screen.fill(COLOR_BG)
        
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        off_x = SCREEN_WIDTH // 2 - cam_x
        off_y = SCREEN_HEIGHT // 2 - cam_y

        # 타일 그리기 루프 (MAP_LIMIT까지 정확히 포함)
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                pts = [iso_projection(x+dx, y+dy) for dx, dy in [(0,0), (TILE_SIZE,0), (TILE_SIZE,TILE_SIZE), (0,TILE_SIZE)]]
                render_pts = [(p[0] + off_x, p[1] + off_y) for p in pts]
                
                # 화면 컬링 및 그리기
                if -200 < render_pts[0][0] < SCREEN_WIDTH + 200 and -200 < render_pts[0][1] < SCREEN_HEIGHT + 200:
                    # 맵의 끝 타일은 붉은색 선으로 표시하여 경계 확인
                    color = COLOR_BORDER if (x == 0 or y == 0 or x + TILE_SIZE >= MAP_LIMIT or y + TILE_SIZE >= MAP_LIMIT) else COLOR_TILE
                    pygame.draw.polygon(screen, color, render_pts, 1)

        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()