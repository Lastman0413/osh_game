import pygame
import math

# --- 1. 전역 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 맵 설정: 15x15 타일 월드
TILE_SIZE = 60
MAP_TILES = 15
MAP_LIMIT = TILE_SIZE * MAP_TILES

# 색상
COLOR_BG = (255, 255, 255)
COLOR_TILE = (180, 180, 180)
COLOR_PLAYER = (0, 0, 0)

# --- 2. 수학 유틸리티 ---
def iso_projection(x, y):
    """2:1 비율의 쿼터뷰 좌표 변환"""
    return (x - y), (x + y) / 2

# --- 3. 플레이어 클래스 ---
class Player:
    def __init__(self):
        # 맵의 정중앙에서 시작 (월드 좌표)
        self.world_pos = pygame.Vector2(MAP_LIMIT // 2, MAP_LIMIT // 2)
        self.speed = 5
        self.walk_count = 0
        
        # 선 기반 신체 규격
        self.head_r = 12
        self.body_w, self.body_h = 22, 35
        self.limb_len = 25
        self.line_thickness = 3

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        
        # 쿼터뷰 조작 보정 (W=북, S=남, A=서, D=동)
        if keys[pygame.K_w]: move.y -= 1; move.x -= 1
        if keys[pygame.K_s]: move.y += 1; move.x += 1
        if keys[pygame.K_a]: move.x -= 1; move.y += 1
        if keys[pygame.K_d]: move.x += 1; move.y -= 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            next_pos = self.world_pos + move
            
            # --- 맵 경계 제한 ---
            if 0 <= next_pos.x <= MAP_LIMIT:
                self.world_pos.x = next_pos.x
            if 0 <= next_pos.y <= MAP_LIMIT:
                self.world_pos.y = next_pos.y
                
            self.walk_count += 0.15
        else:
            self.walk_count = 0

    def draw(self, surface):
        # 캐릭터는 화면 중앙(Screen Center)에 고정 렌더링
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        swing = math.sin(self.walk_count) * 12
        
        # 1. 다리 (선 기반)
        pygame.draw.line(surface, COLOR_PLAYER, (cx - 6, cy + 5), 
                         (cx - 6 - swing/2, cy + 5 + self.limb_len + swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + 6, cy + 5), 
                         (cx + 6 + swing/2, cy + 5 + self.limb_len - swing), self.line_thickness)
        
        # 2. 몸통
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 30, self.body_w, self.body_h), 2)
        
        # 3. 팔 (선 기반)
        pygame.draw.line(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 25), 
                         (cx - self.body_w//2 - 10, cy - 25 + self.limb_len - swing), self.line_thickness)
        pygame.draw.line(surface, COLOR_PLAYER, (cx + self.body_w//2, cy - 25), 
                         (cx + self.body_w//2 + 10, cy - 25 + self.limb_len + swing), self.line_thickness)
        
        # 4. 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, cy - 42), self.head_r, 2)

# --- 4. 메인 게임 루프 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Integrated Zomboid Prototype")
    clock = pygame.time.Clock()
    
    player = Player()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 데이터 업데이트
        player.update()
        
        # 화면 그리기 시작
        screen.fill(COLOR_BG)
        
        # 카메라 오프셋 계산 (화면 중앙 - 플레이어의 쿼터뷰 월드 위치)
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        off_x = SCREEN_WIDTH // 2 - cam_x
        off_y = SCREEN_HEIGHT // 2 - cam_y

        # 맵 타일 렌더링
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                # 각 타일의 네 꼭짓점 변환
                pts = [iso_projection(x+dx, y+dy) for dx, dy in [(0,0), (TILE_SIZE,0), (TILE_SIZE,TILE_SIZE), (0,TILE_SIZE)]]
                render_pts = [(p[0] + off_x, p[1] + off_y) for p in pts]
                
                # 최적화: 화면 안에 보일 때만 그리기
                if -100 < render_pts[0][0] < SCREEN_WIDTH + 100 and -100 < render_pts[0][1] < SCREEN_HEIGHT + 100:
                    pygame.draw.polygon(screen, COLOR_TILE, render_pts, 1)

        # 고정된 플레이어 그리기
        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()