# 기본 캐릭터 생성(점으로 표현함)

import pygame

# --- 설정값 (Config) ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40  # 좀보이드의 타일 느낌을 내기 위한 기본 단위

# 색상 정의
COLOR_BG = (30, 30, 30)   # 어두운 아스팔트 느낌
COLOR_PLAYER = (50, 120, 50) # 생존자 느낌의 국방색
COLOR_GRID = (50, 50, 50)

class Player:
    def __init__(self):
        # 화면 중앙에서 시작
        self.pos = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 4
        self.size = 30

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        # 대각선 이동 속도 보정 (안 하면 대각선이 더 빠름)
        if move.length() > 0:
            move = move.normalize() * self.speed
        
        self.pos += move

    def draw(self, surface):
        # 캐릭터를 사각형으로 임시 구현 (이후 이미지로 교체)
        rect = pygame.Rect(self.pos.x - self.size//2, self.pos.y - self.size//2, self.size, self.size)
        pygame.draw.rect(surface, COLOR_PLAYER, rect)
        # 앞을 보는 방향 표시 (마우스 방향 응용 가능)
        pygame.draw.rect(surface, (200, 200, 200), rect, 2)

class Map:
    def __init__(self):
        self.tile_size = TILE_SIZE

    def draw(self, surface):
        # 격자를 그려서 거리감을 제공 (실제 게임에선 텍스처 타일)
        for x in range(0, SCREEN_WIDTH, self.tile_size):
            pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, self.tile_size):
            pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

# --- 메인 루프 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zomboid Prototype - Python")
    clock = pygame.time.Clock()

    player = Player()
    world_map = Map()

    running = True
    while running:
        # 1. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. 업데이트
        player.handle_input()

        # 3. 출력
        screen.fill(COLOR_BG)
        world_map.draw(screen) # 배경 먼저
        player.draw(screen)    # 캐릭터 나중에
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()