# 캐릭터 쿼터 뷰로 구현함
# 쿼터뷰 공식은 수학적으로 가장 깔끔한 $2:1$ 투영법을 사용했습니다
# 이 방식은 실제 좀보이드나 고전 RPG(디아블로 1, 2 등)에서 가장 흔히 쓰이는 디메트릭(Dimetric) 투영의 변형입니다.
# 수평 회전: $45^\circ$ (정사각형 타일을 다이아몬드 형태로 회전)수직 기울기(기울임): 약 $30^\circ$ (수학적으로는 $\arcsin(0.5)$에 가깝습니다)
# 코드에서 iso_y = (x + y) / 2 부분을 보십시오. $Y$축 값을 정확히 절반($0.5$배)으로 줄였는데, 
# 이는 화면상에서 가로 2픽셀 이동할 때 세로 1픽셀 이동하는 $2:1$ 비율을 만듭니다. 
# 이 비율이 픽셀 아트로 그렸을 때 계단 현상이 적고 가장 보기 편안한 각도를 제공합니다.
# 



import pygame
import math

# --- 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상
COLOR_TILE = (70, 70, 70)
COLOR_GRID = (100, 100, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 쿼터뷰 변환 함수 (핵심 수학 공식)
def iso_projection(x, y, z=0):
    # 45도 회전 및 축소 투영
    iso_x = (x - y)
    iso_y = (x + y) / 2 - z  # z는 높이값 (점프나 층수를 표현할 때)
    return int(iso_x), int(iso_y)

class Player:
    def __init__(self):
        # 내부적인 '실제' 좌표 (논리적 위치)
        self.logic_pos = pygame.Vector2(0, 0)
        self.speed = 3
        self.walk_count = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            self.logic_pos += move
            self.walk_count += 0.2
        else:
            self.walk_count = 0

    def draw(self, surface, offset_x, offset_y):
        # 1. 논리 좌표를 쿼터뷰 화면 좌표로 변환
        screen_x, screen_y = iso_projection(self.logic_pos.x, self.logic_pos.y)
        render_x = screen_x + offset_x
        render_y = screen_y + offset_y

        # 애니메이션 값
        swing = math.sin(self.walk_count) * 10

        # 2. 쿼터뷰 스타일로 캐릭터 그리기 (머리, 몸통, 팔다리)
        # 다리
        pygame.draw.line(surface, BLACK, (render_x - 5, render_y), (render_x - 5, render_y + 20 + swing), 2)
        pygame.draw.line(surface, BLACK, (render_x + 5, render_y), (render_x + 5, render_y + 20 - swing), 2)
        # 몸통
        pygame.draw.rect(surface, BLACK, (render_x - 10, render_y - 30, 20, 30), 2)
        # 머리
        pygame.draw.circle(surface, BLACK, (render_x, render_y - 40), 12, 2)
        # 팔
        pygame.draw.line(surface, BLACK, (render_x - 12, render_y - 25), (render_x - 12, render_y - 10 - swing), 2)
        pygame.draw.line(surface, BLACK, (render_x + 12, render_y - 25), (render_x + 12, render_y - 10 + swing), 2)

def draw_iso_grid(surface, offset_x, offset_y):
    # 바닥에 마름모꼴 타일 깔기 (좀보이드 느낌의 기본)
    tile_size = 40
    for x in range(0, 400, tile_size):
        for y in range(0, 400, tile_size):
            # 타일의 네 꼭짓점을 쿼터뷰로 변환
            p1 = iso_projection(x, y)
            p2 = iso_projection(x + tile_size, y)
            p3 = iso_projection(x + tile_size, y + tile_size)
            p4 = iso_projection(x, y + tile_size)
            
            points = [(p[0] + offset_x, p[1] + offset_y) for p in [p1, p2, p3, p4]]
            pygame.draw.polygon(surface, COLOR_GRID, points, 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    player = Player()
    # 화면 중앙을 기준으로 쿼터뷰 원점 설정
    offset_x, offset_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.handle_input()
        screen.fill(WHITE)
        
        draw_iso_grid(screen, offset_x, offset_y)
        player.draw(screen, offset_x, offset_y)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()