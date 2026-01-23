import pygame
import math

# --- 1. 설정 및 색상 정의 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

TILE_SIZE = 60
MAP_TILES = 40 
MAP_LIMIT = TILE_SIZE * MAP_TILES

# 테마 색상
COLOR_OUTSIDE = (255, 255, 255)  # 맵 외부 (흰색)
COLOR_ASPHALT = (50, 50, 50)     # 아스팔트 타일
COLOR_LIGHT_GRID = (200, 200, 200) # 연한 회색 격자
COLOR_BORDER_LINE = (255, 0, 0)  # 맵 끝 경계선 (빨간색)

# 캐릭터 색상
COLOR_HEAD = (255, 203, 164)     # 복숭아색
COLOR_BODY = (135, 206, 235)     # 하늘색
COLOR_LIMB = (255, 255, 255)     # 팔다리 (흰색)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.speed = 7
        self.walk_count = 0
        
        self.limb_len = 22 
        self.body_h = 35   
        self.head_r = 12
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
        
        # 1. 다리 (흰색)
        pygame.draw.line(surface, COLOR_LIMB, (cx - 6, pelvis_y), (cx - 6 - swing/2, cy + swing/2), self.line_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 6, pelvis_y), (cx + 6 + swing/2, cy - swing/2), self.line_thickness)
        
        # 2. 몸통 (하늘색 채우기)
        body_rect = (cx - 11, pelvis_y - self.body_h, 22, self.body_h)
        pygame.draw.rect(surface, COLOR_BODY, body_rect) # 면 채우기
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 1) # 테두리
        
        # 3. 팔 (흰색)
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_LIMB, (cx - 11, shoulder_y), (cx - 20, shoulder_y + 20 - swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 11, shoulder_y), (cx + 20, shoulder_y + 20 + swing), self.line_thickness)
        
        # 4. 머리 (복숭아색 채우기)
        head_center = (cx, shoulder_y - 12)
        pygame.draw.circle(surface, COLOR_HEAD, head_center, self.head_r) # 면 채우기
        pygame.draw.circle(surface, (255, 255, 255), head_center, self.head_r, 1) # 테두리

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Colorful Survivor on Asphalt World")
    clock = pygame.time.Clock()
    player = Player()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        player.update()
        
        # 맵 외부를 흰색으로 채움
        screen.fill(COLOR_OUTSIDE)
        
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        off_x = SCREEN_WIDTH // 2 - cam_x
        off_y = SCREEN_HEIGHT // 2 - cam_y

        # 맵 렌더링
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                p_iso = iso_projection(x, y)
                screen_x = p_iso[0] + off_x
                screen_y = p_iso[1] + off_y
                
                # 가시성 체크
                if -150 < screen_x < SCREEN_WIDTH + 150 and -150 < screen_y < SCREEN_HEIGHT + 150:
                    pts = [iso_projection(x+dx, y+dy) for dx, dy in [(0,0), (TILE_SIZE,0), (TILE_SIZE,TILE_SIZE), (0,TILE_SIZE)]]
                    render_pts = [(p[0] + off_x, p[1] + off_y) for p in pts]
                    
                    # 아스팔트 타일 채우기
                    pygame.draw.polygon(screen, COLOR_ASPHALT, render_pts)
                    
                    # 격자선 (연한 회색) 및 최외곽 경계선 처리
                    is_border = (x == 0 or y == 0 or x + TILE_SIZE >= MAP_LIMIT or y + TILE_SIZE >= MAP_LIMIT)
                    grid_color = COLOR_BORDER_LINE if is_border else COLOR_LIGHT_GRID
                    pygame.draw.polygon(screen, grid_color, render_pts, 1)

        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()