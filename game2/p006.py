import pygame
import math

# --- 1. 전역 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 맵 설정: 40x40 타일 (기존 10x10의 16배 면적)
TILE_SIZE = 60
MAP_TILES = 40 
MAP_LIMIT = TILE_SIZE * MAP_TILES # 2400px

# 색상 (아스팔트 테마)
COLOR_BG = (30, 30, 30)          # 배경 (맵 바깥 공백)
COLOR_ASPHALT = (50, 50, 50)     # 아스팔트 타일 면
COLOR_GRID = (70, 70, 70)        # 타일 경계선
COLOR_BORDER = (150, 50, 50)     # 최외곽 경계선
COLOR_PLAYER = (255, 255, 255)   # 캐릭터 (어두운 배경 대비 흰색/밝은색)

def iso_projection(x, y):
    """2:1 투영 공식"""
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.speed = 7 # 맵이 넓어졌으므로 속도를 약간 상향
        self.walk_count = 0
        
        # 이전 합의된 비율 (다리 22px)
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
            self.world_pos.x = max(0, min(next_pos.x, MAP_LIMIT))
            self.world_pos.y = max(0, min(next_pos.y, MAP_LIMIT))
            self.walk_count += 0.2
        else:
            self.walk_count = 0

    def draw(self, surface):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 10 
        
        pelvis_y = cy - self.limb_len
        
        # 캐릭터 색상을 밝게 변경 (아스팔트에서 잘 보이도록)
        # 다리
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 6, pelvis_y), (cx - 6 - swing/2, cy + swing/2), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 6, pelvis_y), (cx + 6 + swing/2, cy - swing/2), self.line_thickness)
        # 몸통
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - 11, pelvis_y - self.body_h, 22, self.body_h), 2)
        # 팔
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 11, shoulder_y), (cx - 20, shoulder_y + 20 - swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 11, shoulder_y), (cx + 20, shoulder_y + 20 + swing), self.line_thickness)
        # 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, shoulder_y - 12), 12, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Expanded Asphalt World (40x40)")
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

        # 맵 렌더링 (Culling 최적화 강화)
        # 화면에 보이는 범위만 계산하여 성능 저하 방지
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                p_iso = iso_projection(x, y)
                screen_x = p_iso[0] + off_x
                screen_y = p_iso[1] + off_y
                
                # 화면 안팎 검사 (여유값 150px)
                if -150 < screen_x < SCREEN_WIDTH + 150 and -150 < screen_y < SCREEN_HEIGHT + 150:
                    pts = [iso_projection(x+dx, y+dy) for dx, dy in [(0,0), (TILE_SIZE,0), (TILE_SIZE,TILE_SIZE), (0,TILE_SIZE)]]
                    render_pts = [(p[0] + off_x, p[1] + off_y) for p in pts]
                    
                    # 아스팔트 채우기
                    pygame.draw.polygon(screen, COLOR_ASPHALT, render_pts)
                    # 격자 선 그리기
                    color = COLOR_BORDER if (x == 0 or y == 0 or x + TILE_SIZE >= MAP_LIMIT or y + TILE_SIZE >= MAP_LIMIT) else COLOR_GRID
                    pygame.draw.polygon(screen, color, render_pts, 1)

        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()