import pygame
import math

# --- 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상
COLOR_TILE_BORDER = (100, 100, 100)
COLOR_PLAYER = (0, 0, 0)
WHITE = (255, 255, 255)

def iso_projection(x, y):
    # 2:1 투영법 공식
    iso_x = (x - y)
    iso_y = (x + y) / 2
    return iso_x, iso_y

class Player:
    def __init__(self):
        self.world_pos = pygame.Vector2(0, 0)
        self.speed = 5
        self.walk_count = 0
        
        # 신체 규격
        self.head_r = 12
        self.body_w, self.body_h = 20, 32
        self.limb_w, self.limb_h = 8, 28

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        
        # 쿼터뷰 조작 보정 (W가 화면 위쪽을 향하도록)
        if keys[pygame.K_w]: move.y -= 1; move.x -= 1
        if keys[pygame.K_s]: move.y += 1; move.x += 1
        if keys[pygame.K_a]: move.x -= 1; move.y += 1
        if keys[pygame.K_d]: move.x += 1; move.y -= 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            self.world_pos += move
            self.walk_count += 0.2
        else:
            self.walk_count = 0

    def draw(self, surface):
        # 캐릭터는 화면 정중앙에 고정
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # 이동 시 흔들림 효과 (sin 함수)
        swing = math.sin(self.walk_count) * 8
        
        # 1. 다리 (몸통 뒤 레이어)
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - 8, cy + swing, self.limb_w, self.limb_h), 2) # 왼다리
        pygame.draw.rect(surface, COLOR_PLAYER, (cx + 2, cy - swing, self.limb_w, self.limb_h), 2) # 오른다리

        # 2. 몸통
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - self.body_w//2, cy - 25, self.body_w, self.body_h), 2)

        # 3. 팔 (누락된 부분 복구)
        # 왼쪽 팔 (다리와 반대로 흔들림)
        pygame.draw.rect(surface, COLOR_PLAYER, (cx - self.body_w//2 - self.limb_w, cy - 20 - swing, self.limb_w, self.limb_h), 2)
        # 오른쪽 팔
        pygame.draw.rect(surface, COLOR_PLAYER, (cx + self.body_w//2, cy - 20 + swing, self.limb_w, self.limb_h), 2)

        # 4. 머리
        pygame.draw.circle(surface, COLOR_PLAYER, (cx, cy - 35), self.head_r, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zomboid Camera & Full Body Prototype")
    clock = pygame.time.Clock()
    
    player = Player()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update()
        screen.fill(WHITE)
        
        # 카메라 오프셋 계산 (캐릭터의 월드 위치 기반)
        cam_x, cam_y = iso_projection(player.world_pos.x, player.world_pos.y)
        offset_x = SCREEN_WIDTH // 2 - cam_x
        offset_y = SCREEN_HEIGHT // 2 - cam_y

        # 타일 그리기 (성능을 위해 캐릭터 주변만 그림)
        tile_size = 60
        for x in range(-1200, 1200, tile_size):
            for y in range(-1200, 1200, tile_size):
                p1 = iso_projection(x, y)
                p2 = iso_projection(x + tile_size, y)
                p3 = iso_projection(x + tile_size, y + tile_size)
                p4 = iso_projection(x, y + tile_size)
                
                points = [(p[0] + offset_x, p[1] + offset_y) for p in [p1, p2, p3, p4]]
                
                # 화면 바깥 타일은 그리지 않는 기초적인 컬링(Culling)
                if -100 < points[0][0] < SCREEN_WIDTH + 100 and -100 < points[0][1] < SCREEN_HEIGHT + 100:
                    pygame.draw.polygon(screen, COLOR_TILE_BORDER, points, 1)

        # 고정된 캐릭터 그리기
        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()