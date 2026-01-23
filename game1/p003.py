import pygame
import sys
import math
import random

# --- 초기 설정 및 색상 추가 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
CHAR_SIZE = 32

# 캐릭터 색상
SKIN, HAIR, TOP, PANTS = (235, 195, 165), (80, 50, 40), (70, 80, 60), (50, 55, 70)
# 좀비 색상 (창백하고 오염된 느낌)
ZOMBIE_SKIN = (160, 180, 160)
ZOMBIE_TOP = (60, 60, 70)
BG_COLOR = (40, 45, 40)

class Survivor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.state, self.direction = "IDLE", "DOWN"
        self.is_sitting = False
        self.hp = 100
        self.rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, CHAR_SIZE, CHAR_SIZE)
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 3
        self.frame = 0
        self.last_anim_update = pygame.time.get_ticks()

    def create_surface(self):
        surf = pygame.Surface((CHAR_SIZE, CHAR_SIZE), pygame.SRCALPHA)
        offset_y = 6 if self.is_sitting else 0
        h_mod = -4 if self.is_sitting else 0
        
        # 데미지 입었을 때 깜빡임 효과 (선택사항)
        color_mod = (255, 0, 0) if self.hp < 30 and pygame.time.get_ticks() % 200 < 100 else (0,0,0,0)

        pygame.draw.rect(surf, HAIR, (12, 4 + offset_y, 8, 8))
        pygame.draw.rect(surf, SKIN, (13, 8 + offset_y, 6, 4))
        pygame.draw.rect(surf, TOP, (10, 12 + offset_y, 12, 10 + h_mod))
        pygame.draw.rect(surf, PANTS, (10, 22 + offset_y, 12, 8 + h_mod))
        return surf

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        self.is_sitting = keys[pygame.K_s]

        if not self.is_sitting and self.hp > 0:
            if keys[pygame.K_LEFT]: dx = -self.speed
            elif keys[pygame.K_RIGHT]: dx = self.speed
            if keys[pygame.K_UP]: dy = -self.speed
            elif keys[pygame.K_DOWN]: dy = self.speed
            
            self.state = "WALK" if dx != 0 or dy != 0 else "IDLE"
            self.pos.x += dx
            self.pos.y += dy
            self.rect.center = self.pos

        now = pygame.time.get_ticks()
        if now - self.last_anim_update > 150:
            self.frame = (self.frame + 1) % 2
            self.last_anim_update = now
        self.image = self.create_surface()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target # 쫓아갈 대상(Survivor)
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), CHAR_SIZE, CHAR_SIZE)
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 1.2 # 플레이어보다 느림 (좀보이드 기본 설정)
        self.image = self.create_zombie_surface()

    def create_zombie_surface(self):
        surf = pygame.Surface((CHAR_SIZE, CHAR_SIZE), pygame.SRCALPHA)
        # 좀비 실루엣 (약간 구부정한 느낌을 위해 위치 조정)
        pygame.draw.rect(surf, (50, 60, 50), (12, 6, 8, 8))  # 머리카락/머리
        pygame.draw.rect(surf, ZOMBIE_SKIN, (13, 10, 6, 4))  # 얼굴
        pygame.draw.rect(surf, ZOMBIE_TOP, (10, 14, 12, 12)) # 몸통
        pygame.draw.rect(surf, (40, 40, 50), (10, 26, 12, 6)) # 바지
        return surf

    def update(self):
        # 플레이어 방향으로 벡터 이동
        if self.target.hp > 0:
            direction_vec = self.target.pos - self.pos
            if direction_vec.length() > 0:
                direction_vec = direction_vec.normalize()
                self.pos += direction_vec * self.speed
                self.rect.center = self.pos

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    player = Survivor()
    # 좀비 여러 마리 관리 가능하도록 그룹화
    zombies = pygame.sprite.Group()
    for _ in range(3): # 일단 3마리 소환
        zombies.add(Zombie(player))
        
    all_sprites = pygame.sprite.Group(player, *zombies)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        all_sprites.update()

        # --- 충돌 감지 로직 (비판적 검토: 매 프레임 체크) ---
        hits = pygame.sprite.spritecollide(player, zombies, False)
        if hits and not player.is_sitting:
            player.hp -= 0.5 # 접촉 시 서서히 체력 감소
            if player.hp <= 0:
                player.hp = 0
                print("당신은 좀비의 밥이 되었습니다.")

        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        
        # HP 바 표시 (생존 게임의 기본)
        pygame.draw.rect(screen, (255, 0, 0), (20, 50, 100, 10))
        pygame.draw.rect(screen, (0, 255, 0), (20, 50, player.hp, 10))
        
        font = pygame.font.SysFont(None, 24)
        msg = "ZOMBOID TEST - Don't let them touch you!" if player.hp > 0 else "YOU ARE DEAD"
        screen.blit(font.render(msg, True, (255, 255, 255)), (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()