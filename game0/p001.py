import pygame
import math

# --- 설정 (기존 설정 유지) ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 60
MAP_TILES = 40 
MAP_LIMIT = TILE_SIZE * MAP_TILES

COLOR_OUTSIDE = (255, 255, 255)
COLOR_ASPHALT = (50, 50, 50)
COLOR_LIGHT_GRID = (200, 200, 200)
COLOR_HEAD = (255, 203, 164)
COLOR_BODY = (135, 206, 235)
COLOR_LIMB = (255, 255, 255)
COLOR_BACKPACK = (85, 107, 47) # 올리브 드랍 (가방 색상)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.look_dir = pygame.Vector2(0, 1)
        self.speed = 7
        self.walk_count = 0
        self.limb_len = 22 
        self.body_h = 35   
        self.head_r = 12

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        if move.length() > 0:
            move = move.normalize()
            self.look_dir = move
            next_pos = self.world_pos + move * self.speed
            self.world_pos.x = max(0, min(next_pos.x, MAP_LIMIT))
            self.world_pos.y = max(0, min(next_pos.y, MAP_LIMIT))
            self.walk_count += 0.2
        else:
            self.walk_count = 0

    def draw(self, surface):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 10
        bobbing = abs(math.sin(self.walk_count)) * 3 # 걷을 때 위아래 들썩임
        pelvis_y = cy - self.limb_len
        
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        b_width = 14 if is_side else 22
        
        # 가방 좌표 설정
        bag_w, bag_h = b_width + 4, 25
        bag_rect = (cx - bag_w//2, pelvis_y - self.body_h + 8 + bobbing, bag_w, bag_h)

        # 1. 가방 (뒷모습이 아닐 때 먼저 그리기 - 몸 뒤에 숨김)
        if not is_back:
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect)
            pygame.draw.rect(surface, (0, 0, 0), bag_rect, 1)

        # 2. 다리
        pygame.draw.line(surface, COLOR_LIMB, (cx - 6, pelvis_y), (cx - 6 - swing/2, cy + swing/2), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 6, pelvis_y), (cx + 6 + swing/2, cy - swing/2), 3)

        # 3. 몸통
        body_rect = (cx - b_width//2, pelvis_y - self.body_h, b_width, self.body_h)
        pygame.draw.rect(surface, COLOR_BODY, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 1)

        # 4. 가방 끈 (정면일 때 어깨에 표시)
        if not is_back:
            shoulder_y = pelvis_y - self.body_h + 5
            pygame.draw.line(surface, COLOR_BACKPACK, (cx - b_width//2, shoulder_y), (cx - b_width//2 + 4, shoulder_y + 10), 3)
            pygame.draw.line(surface, COLOR_BACKPACK, (cx + b_width//2, shoulder_y), (cx + b_width//2 - 4, shoulder_y + 10), 3)

        # 5. 가방 (뒷모습일 때 나중에 그리기 - 등을 덮음)
        if is_back:
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect)
            pygame.draw.rect(surface, (0, 0, 0), bag_rect, 1)

        # 6. 팔
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_LIMB, (cx - b_width//2, shoulder_y), (cx - b_width//2 - 8, shoulder_y + 20 - swing), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + b_width//2, shoulder_y), (cx + b_width//2 + 8, shoulder_y + 20 + swing), 3)

        # 7. 머리
        head_y = shoulder_y - 12
        pygame.draw.circle(surface, COLOR_HEAD, (cx, head_y), self.head_r)
        pygame.draw.circle(surface, (255, 255, 255), (cx, head_y), self.head_r, 1)
        
        if not is_back:
            eye_x = cx + (self.look_dir.x * 5)
            eye_y = head_y + (self.look_dir.y * 3)
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x - 3), int(eye_y)), 2)
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x + 3), int(eye_y)), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        player.update()
        screen.fill(COLOR_OUTSIDE)
        
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        off_x, off_y = SCREEN_WIDTH // 2 - cam_x, SCREEN_HEIGHT // 2 - cam_y

        # 최적화된 맵 렌더링
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                p_iso = iso_projection(x, y)
                if -150 < p_iso[0] + off_x < SCREEN_WIDTH + 150 and -150 < p_iso[1] + off_y < SCREEN_HEIGHT + 150:
                    pts = [iso_projection(x+dx, y+dy) for dx, dy in [(0,0), (TILE_SIZE,0), (TILE_SIZE,TILE_SIZE), (0,TILE_SIZE)]]
                    render_pts = [(p[0] + off_x, p[1] + off_y) for p in pts]
                    pygame.draw.polygon(screen, COLOR_ASPHALT, render_pts)
                    pygame.draw.polygon(screen, COLOR_LIGHT_GRID, render_pts, 1)

        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()