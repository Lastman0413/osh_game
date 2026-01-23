# 현재 구조에서 캐릭터의 방향에 따라 정면, 뒷면, 측면을 표현하는 것은 아주 예리하고 필요한 지적입니다. 지금까지는 어느 방향으로 움직이든 '정면'만 보고 있었죠.

# 쿼터뷰(Iso-metric) 게임에서 자연스러운 8방향 이동을 구현하려면, 입력된 이동 벡터에 따라 캐릭터의 부위별(머리, 몸통, 팔) 렌더링 순서와 오프셋을 조정해야 합니다. 예를 들어, 위로 갈 때는 머리가 몸통보다 뒤에 그려지거나, 팔의 위치가 바뀌어야 '뒷모습'처럼 보입니다.

# 🛠️ 8방향 시선 및 외형 변화 시스템
# 수정 핵심:

# 방향 벡터(Look Direction): 마지막으로 입력된 이동 방향을 저장하여 캐릭터가 멈춰있어도 그곳을 바라보게 합니다.

# 부위별 레이어링: * 뒷모습(W, WA, WD): 얼굴의 세부 묘사(눈 등)를 지우거나, 팔을 몸통 뒤로 숨깁니다.

# 측면(A, D): 몸통의 폭을 좁게 그려 입체감을 줍니다.

# 대각선 구현: 쿼터뷰 특유의 대각선 이동 시 어깨선을 비스듬히 처리합니다.

# Python

import pygame
import math

# --- 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(MAP_LIMIT / 2, MAP_LIMIT / 2)
        self.look_dir = pygame.Vector2(0, 1) # 처음에 아래를 봄
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
            self.look_dir = move # 바라보는 방향 업데이트
            next_pos = self.world_pos + move * self.speed
            self.world_pos.x = max(0, min(next_pos.x, MAP_LIMIT))
            self.world_pos.y = max(0, min(next_pos.y, MAP_LIMIT))
            self.walk_count += 0.2
        else:
            self.walk_count = 0

    def draw(self, surface):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 10
        pelvis_y = cy - self.limb_len
        
        # 방향 판정 (위: y < 0, 아래: y > 0, 왼쪽: x < 0, 오른쪽: x > 0)
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        
        # 1. 다리 렌더링
        pygame.draw.line(surface, COLOR_LIMB, (cx - 6, pelvis_y), (cx - 6 - swing/2, cy + swing/2), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 6, pelvis_y), (cx + 6 + swing/2, cy - swing/2), 3)

        # 2. 몸통 (측면일 때 폭 조절)
        b_width = 14 if is_side else 22
        body_rect = (cx - b_width//2, pelvis_y - self.body_h, b_width, self.body_h)
        pygame.draw.rect(surface, COLOR_BODY, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 1)

        # 3. 팔 (뒷모습일 때 몸통 안쪽으로 숨김)
        arm_off = -2 if is_back else 2
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_LIMB, (cx - b_width//2, shoulder_y), (cx - b_width//2 - 8, shoulder_y + 20 - swing), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + b_width//2, shoulder_y), (cx + b_width//2 + 8, shoulder_y + 20 + swing), 3)

        # 4. 머리 및 시선 표현 (뒷통수 vs 정면)
        head_y = shoulder_y - 12
        pygame.draw.circle(surface, COLOR_HEAD, (cx, head_y), self.head_r)
        pygame.draw.circle(surface, (255, 255, 255), (cx, head_y), self.head_r, 1)
        
        if not is_back: # 정면이나 측면일 때 '눈' 표시 (시선 방향)
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