# 사람모양으로 조정함 평면에서 구현

import pygame
import math

# --- 설정값 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 4
        self.walk_count = 0  # 애니메이션 타이머
        
        # 신체 규격
        self.head_r = 15
        self.body_w, self.body_h = 24, 40
        self.limb_w, self.limb_h = 10, 35 # 팔다리 공통 규격

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        is_moving = False

        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            self.pos += move
            is_moving = True
            self.walk_count += 0.2  # 이동 중일 때만 애니메이션 진행
        else:
            # 멈춰있을 때는 서서히 기본 자세로 복귀
            self.walk_count = 0 

    def draw(self, surface):
        x, y = int(self.pos.x), int(self.pos.y)
        
        # 애니메이션 값 (sin 함수를 이용해 -1 ~ 1 사이를 왕복)
        # 팔과 다리는 서로 반대로 움직여야 하므로 offset을 줌
        swing = math.sin(self.walk_count) * 15 

        # 1. 다리 그리기 (몸통 뒤에 와야 하므로 먼저 그림)
        # 왼쪽 다리 (swing)
        pygame.draw.rect(surface, BLACK, (x - 12, y + self.body_h + swing//2, self.limb_w, self.limb_h), 2)
        # 오른쪽 다리 (-swing)
        pygame.draw.rect(surface, BLACK, (x + 2, y + self.body_h - swing//2, self.limb_w, self.limb_h), 2)

        # 2. 몸통
        pygame.draw.rect(surface, BLACK, (x - self.body_w//2, y, self.body_w, self.body_h), 2)

        # 3. 머리
        pygame.draw.circle(surface, BLACK, (x, y - self.head_r), self.head_r, 2)

        # 4. 팔 그리기 (몸통 옆)
        # 왼쪽 팔 (-swing: 다리와 반대로 움직이는 게 자연스러움)
        pygame.draw.rect(surface, BLACK, (x - self.body_w//2 - self.limb_w, y - swing//2, self.limb_w, self.limb_h), 2)
        # 오른쪽 팔 (swing)
        pygame.draw.rect(surface, BLACK, (x + self.body_w//2, y + swing//2, self.limb_w, self.limb_h), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Animated Survivor Prototype")
    clock = pygame.time.Clock()
    
    player = Player()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.handle_input()

        screen.fill(WHITE)
        
        # 격자 배경 (공간감 제공)
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (240, 240, 240), (i, 0), (i, SCREEN_HEIGHT))
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (240, 240, 240), (0, i), (SCREEN_WIDTH, i))

        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()