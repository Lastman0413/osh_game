import pygame
import sys

# --- 초기 설정 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
CHAR_SIZE = 32

# 좀보이드 여캐 느낌의 색상 팔레트 (생존자 룩)
SKIN = (235, 195, 165)      # 피부색
HAIR = (80, 50, 40)         # 갈색 머리
TOP = (70, 80, 60)          # 국방색 셔츠/재킷
PANTS = (50, 55, 70)        # 데님 팬츠
BG_COLOR = (40, 45, 40)     # 좀보이드 특유의 어두운 숲/도시 느낌

class Survivor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.state = "IDLE"      # IDLE, WALK, SIT
        self.direction = "DOWN"
        self.is_sitting = False
        
        # 위치 설정
        self.rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, CHAR_SIZE, CHAR_SIZE)
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 3
        self.frame = 0
        self.last_anim_update = pygame.time.get_ticks()

    def create_surface(self, state, direction, frame):
        """좀보이드 여캐 실루엣을 흉내 내는 절차적 그래픽 생성"""
        surf = pygame.Surface((CHAR_SIZE, CHAR_SIZE), pygame.SRCALPHA)
        
        # 앉아 있을 때와 서 있을 때의 높이 조절
        offset_y = 6 if state == "SIT" else 0
        h_mod = -4 if state == "SIT" else 0 # 앉으면 키가 작아짐

        # 1. 머리카락 & 머리 (위쪽)
        pygame.draw.rect(surf, HAIR, (12, 4 + offset_y, 8, 8)) # 머리통
        pygame.draw.rect(surf, SKIN, (13, 8 + offset_y, 6, 4)) # 얼굴 부분

        # 2. 몸통 (상의)
        body_h = 10 + h_mod
        pygame.draw.rect(surf, TOP, (10, 12 + offset_y, 12, body_h))
        
        # 3. 하의 (다리)
        if state != "SIT":
            # 걷기 프레임에 따른 다리 움직임 묘사
            leg_off = 2 if frame == 1 else -2
            pygame.draw.rect(surf, PANTS, (10, 22 + offset_y, 5, 8 + leg_off))
            pygame.draw.rect(surf, PANTS, (17, 22 + offset_y, 5, 8 - leg_off))
        else:
            # 앉아 있을 때는 다리를 접은 모양
            pygame.draw.rect(surf, PANTS, (8, 22 + offset_y, 16, 6))

        return surf

    def update(self):
        keys = pygame.key.get_pressed()
        old_state = self.state
        
        # --- 상태 결정 ---
        moving = False
        dx, dy = 0, 0

        # 앉기 토글 (S 키)
        if keys[pygame.K_s]:
            self.is_sitting = True
            self.state = "SIT"
        else:
            self.is_sitting = False

        if not self.is_sitting:
            if keys[pygame.K_LEFT]:
                dx, self.direction, moving = -self.speed, "LEFT", True
            elif keys[pygame.K_RIGHT]:
                dx, self.direction, moving = self.speed, "RIGHT", True
            elif keys[pygame.K_UP]:
                dy, self.direction, moving = -self.speed, "UP", True
            elif keys[pygame.K_DOWN]:
                dy, self.direction, moving = self.speed, "DOWN", True
            
            self.state = "WALK" if moving else "IDLE"
        
        # 위치 이동
        self.pos.x += dx
        self.pos.y += dy
        self.rect.center = self.pos

        # --- 애니메이션 프레임 제어 ---
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > 150:
            self.frame = (self.frame + 1) % 2 # 0, 1 반복
            self.last_anim_update = now

        # 현재 상태에 맞는 이미지 생성 (실제 게임에선 로드된 이미지 사용)
        self.image = self.create_surface(self.state, self.direction, self.frame)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Zomboid Style Test (32px)")
    clock = pygame.time.Clock()
    
    survivor = Survivor()
    all_sprites = pygame.sprite.Group(survivor)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        all_sprites.update()

        screen.fill(BG_COLOR)
        # 가이드라인 (바닥 느낌)
        for i in range(0, SCREEN_WIDTH, 64):
            pygame.draw.line(screen, (50, 55, 50), (i, 0), (i, SCREEN_HEIGHT))
            pygame.draw.line(screen, (50, 55, 50), (0, i), (SCREEN_WIDTH, i))

        all_sprites.draw(screen)
        
        # 조작법 표시
        font = pygame.font.SysFont(None, 24)
        img = font.render("Move: Arrow Keys | Sit: Hold 'S'", True, (200, 200, 200))
        screen.blit(img, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()