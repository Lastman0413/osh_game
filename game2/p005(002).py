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
COLOR_BORDER = (255, 0, 0) # 경계는 확실하게 빨간색
COLOR_PLAYER = (0, 0, 0)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.speed = 5
        self.walk_count = 0
        
        # 신체 규격
        self.limb_len = 25 # 다리 길이
        self.body_h = 35   # 몸통 높이

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
            
            # [수정] 경계 처리 로직: 0에서 MAP_LIMIT까지만 허용
            # 이 수치를 조절하면 경계 안쪽으로 더 밀어넣을 수 있음
            self.world_pos.x = max(0, min(next_pos.x, MAP_LIMIT))
            self.world_pos.y = max(0, min(next_pos.y, MAP_LIMIT))
            self.walk_count += 0.15
        else:
            self.walk_count = 0

    def draw(self, surface):
        # cx, cy는 플레이어의 발바닥 위치가 되어야 함
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 12
        
        # 1. 다리: cy(바닥)에서 위로 시작하는 게 아니라, 
        # swing에 따라 바닥을 딛는 느낌으로 수정
        # 무조건 p2의 y좌표가 cy를 넘지 않도록 조정
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 6, cy - 20), (cx - 6 - swing/2, cy + swing), 3) # 왼다리
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 6, cy - 20), (cx + 6 + swing/2, cy - swing), 3) # 오른다리

        # 2. 몸통: 다리 위쪽(cy-20)부터 시작
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - 11, cy - 20 - self.body_h, 22, self.body_h), 2)

        # 3. 팔
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 11, cy - 50), (cx - 20, cy - 30 - swing), 3)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 11, cy - 50), (cx + 20, cy - 30 + swing), 3)

        # 4. 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, cy - 67), 12, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        player.update()
        screen.fill(COLOR_BG)
        
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        off_x = SCREEN_WIDTH // 2 - cam_x
        off_y = SCREEN_HEIGHT // 2 - cam_y

        # 맵 그리기
        for x in range(0, MAP_LIMIT + 1, TILE_SIZE): # 끝선 포함을 위해 +1
            for y in range(0, MAP_LIMIT + 1, TILE_SIZE):
                p1 = iso_projection(x, y)
                p2 = iso_projection(x + TILE_SIZE, y)
                p3 = iso_projection(x + TILE_SIZE, y + TILE_SIZE)
                p4 = iso_projection(x, y + TILE_SIZE)
                
                pts = [(p[0] + off_x, p[1] + off_y) for p in [p1, p2, p3, p4]]
                
                # 경계선 강조
                color = COLOR_BORDER if (x >= MAP_LIMIT - TILE_SIZE or y >= MAP_LIMIT - TILE_SIZE) else COLOR_TILE
                pygame.draw.polygon(screen, color, pts, 1)

        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()