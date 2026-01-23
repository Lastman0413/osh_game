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
COLOR_BORDER = (255, 0, 0)
COLOR_PLAYER = (0, 0, 0)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.speed = 5
        self.walk_count = 0
        
        # [정밀 조정] 최종 다리 길이: 22px (25의 2/3인 17에서 30% 증가)
        self.limb_len = 22 
        self.body_h = 35   
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
            
            # 맵 경계 제한 (0.0 ~ MAP_LIMIT)
            self.world_pos.x = max(0, min(next_pos.x, MAP_LIMIT))
            self.world_pos.y = max(0, min(next_pos.y, MAP_LIMIT))
            self.walk_count += 0.15
        else:
            self.walk_count = 0

    def draw(self, surface):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 10 # 다리 길이에 맞춰 스윙폭 조정
        
        # 1. 다리 (바닥 cy 기준)
        # 골반 위치 계산 (지면 cy에서 다리 길이만큼 위)
        pelvis_y = cy - self.limb_len
        
        # 왼쪽 다리
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 6, pelvis_y), (cx - 6 - swing/2, cy + swing/2), self.line_thickness)
        # 오른쪽 다리
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 6, pelvis_y), (cx + 6 + swing/2, cy - swing/2), self.line_thickness)

        # 2. 몸통 (골반 위로 배치)
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - 11, pelvis_y - self.body_h, 22, self.body_h), 2)

        # 3. 팔 (어깨 위치)
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 11, shoulder_y), (cx - 20, shoulder_y + 20 - swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 11, shoulder_y), (cx + 20, shoulder_y + 20 + swing), self.line_thickness)

        # 4. 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, shoulder_y - 12), 12, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Final Proportions Prototype")
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
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
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