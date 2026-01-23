import pygame
import sys
import math
import random

# --- 1. 환경 설정 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zomboid Environment Test")
clock = pygame.time.Clock()

# 색상 및 환경 설정
BG_COLOR = (35, 40, 35) # 조금 더 진한 숲의 어둠
SKIN, HAIR, TOP, PANTS = (235, 195, 165), (80, 50, 40), (70, 80, 60), (50, 55, 70)
ZOMBIE_SKIN = (140, 160, 140)
BULLET_COLOR = (255, 220, 100)

# --- 2. 배경 요소 클래스 (Environment Detail) ---
class EnvironmentDetail:
    def __init__(self):
        # 화면 안 어디든 랜덤 배치
        self.pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.type = random.choice(['BLOOD', 'GRASS', 'DIRT'])
        self.size = random.randint(15, 40)
        
    def draw(self, surface):
        if self.type == 'BLOOD':
            # 핏자국: 짙은 빨간색, 타원형
            color = (100, 0, 0)
            pygame.draw.ellipse(surface, color, (self.pos[0], self.pos[1], self.size * 1.5, self.size))
        elif self.type == 'GRASS':
            # 마른 풀: 짙은 녹색, 작은 사각형들
            color = (50, 65, 45)
            pygame.draw.rect(surface, color, (self.pos[0], self.pos[1], self.size // 2, self.size))
        elif self.type == 'DIRT':
            # 흙/먼지: 갈색 파편
            color = (60, 55, 50)
            pygame.draw.rect(surface, color, (self.pos[0], self.pos[1], self.size, self.size // 3))

# --- 3. 기본 게임 객체 (Survivor, Zombie, Bullet) ---
# (이전 코드와 동일하되 가독성을 위해 핵심 로직 유지)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.image = pygame.Surface((8, 8)); self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        direction = pygame.Vector2(target_pos) - self.pos
        self.velocity = direction.normalize() * 12 if direction.length() > 0 else pygame.Vector2(1,0)*12
    def update(self):
        self.pos += self.velocity; self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hp, self.ammo, self.weapon_mode = 100, 17, "BAT"
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.pos = pygame.Vector2(self.rect.center)
        self.last_shot = self.last_swing = 0
    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0: self.pos += move.normalize() * 2.2
        self.rect.center = self.pos
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, HAIR, (24, 8, 16, 16))
        pygame.draw.rect(self.image, SKIN, (26, 16, 12, 8))
        pygame.draw.rect(self.image, TOP, (20, 24, 24, 24))
        pygame.draw.rect(self.image, PANTS, (20, 48, 24, 12))
        if self.weapon_mode == "BAT": pygame.draw.line(self.image, (150, 110, 80), (32, 32), (56, 16), 6)
        else: pygame.draw.rect(self.image, (50, 50, 50), (40, 32, 16, 8))

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 70, 60), (24, 12, 16, 16))
        pygame.draw.rect(self.image, ZOMBIE_SKIN, (20, 28, 24, 28))
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), -50))
        self.pos = pygame.Vector2(self.rect.center)
    def update(self):
        dir_vec = self.target.pos - self.pos
        if dir_vec.length() > 0: self.pos += dir_vec.normalize() * 0.8
        self.rect.center = self.pos

# --- 4. 메인 실행 루프 ---

player = Survivor()
all_sprites = pygame.sprite.Group(player)
zombies, bullets = pygame.sprite.Group(), pygame.sprite.Group()

# 배경 요소 50개 미리 생성
details = [EnvironmentDetail() for _ in range(50)]

font = pygame.font.SysFont("arial", 24, bold=True)
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == SPAWN_EVENT and len(zombies) < 15:
            z = Zombie(player); zombies.add(z); all_sprites.add(z)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.weapon_mode = "GLOCK" if player.weapon_mode == "BAT" else "BAT"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            now = pygame.time.get_ticks()
            if player.weapon_mode == "GLOCK" and player.ammo > 0 and now - player.last_shot > 400:
                b = Bullet(player.rect.centerx, player.rect.centery, event.pos)
                bullets.add(b); all_sprites.add(b); player.ammo -= 1; player.last_shot = now
            elif player.weapon_mode == "BAT" and now - player.last_swing > 600:
                player.last_swing = now
                for z in zombies:
                    if player.rect.inflate(40,40).colliderect(z.rect): z.kill()

    if player.hp > 0:
        all_sprites.update()
        pygame.sprite.groupcollide(bullets, zombies, True, True)
        if pygame.sprite.spritecollide(player, zombies, False): player.hp -= 0.15

    # --- 출력 (그리는 순서가 매우 중요합니다) ---
    screen.fill(BG_COLOR) # 1. 배경색
    
    for detail in details: # 2. 배경 디테일 (바닥에 깔려야 함)
        detail.draw(screen)
    
    all_sprites.draw(screen) # 3. 캐릭터 및 좀비 (배경 위에 그려짐)
    
    # UI
    info = font.render(f"HP: {int(player.hp)} | AMMO: {player.ammo}", True, (255, 255, 255))
    screen.blit(info, (20, 20))
    if player.hp <= 0: screen.blit(font.render("GAME OVER", True, (255,0,0)), (400, 350))

    pygame.display.flip()
    clock.tick(FPS)