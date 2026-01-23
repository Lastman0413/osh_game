
import pygame
import sys
import math
import random

# --- 1. 환경 설정 (이 부분이 없어서 에러가 났던 것입니다) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60  # <-- 바로 이 녀석이 범인이었습니다!
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zomboid Survivor Test")
clock = pygame.time.Clock()

# 색상 정의
SKIN, HAIR, TOP, PANTS = (235, 195, 165), (80, 50, 40), (70, 80, 60), (50, 55, 70)
ZOMBIE_SKIN = (140, 160, 140)
BG_COLOR = (40, 45, 40)
BULLET_COLOR = (255, 220, 100)

# --- 2. 클래스 정의 ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        direction = pygame.Vector2(target_pos) - self.pos
        self.velocity = direction.normalize() * 12 if direction.length() > 0 else pygame.Vector2(1,0)*12

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect):
            self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hp = 100
        self.ammo = 17
        self.weapon_mode = "BAT"
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 2.0
        self.last_shot = 0
        self.last_swing = 0

    def draw_player(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, HAIR, (24, 8, 16, 16)) # 머리
        pygame.draw.rect(self.image, SKIN, (26, 16, 12, 8)) # 얼굴
        pygame.draw.rect(self.image, TOP, (20, 24, 24, 24)) # 몸통
        pygame.draw.rect(self.image, PANTS, (20, 48, 24, 12)) # 다리
        if self.weapon_mode == "BAT":
            pygame.draw.line(self.image, (150, 110, 80), (32, 32), (56, 16), 6)
        else:
            pygame.draw.rect(self.image, (50, 50, 50), (40, 32, 16, 8))

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0:
            self.pos += move.normalize() * self.speed
        self.rect.center = self.pos
        self.rect.clamp_ip(screen.get_rect())
        self.draw_player()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 70, 60), (24, 12, 16, 16))
        pygame.draw.rect(self.image, ZOMBIE_SKIN, (20, 28, 24, 28))
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T': x, y = random.randint(0, SCREEN_WIDTH), -50
        elif side == 'B': x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT+50
        elif side == 'L': x, y = -50, random.randint(0, SCREEN_HEIGHT)
        else: x, y = SCREEN_WIDTH+50, random.randint(0, SCREEN_HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 0.8

    def update(self):
        if self.target.hp > 0:
            dir_vec = self.target.pos - self.pos
            if dir_vec.length() > 0:
                self.pos += dir_vec.normalize() * self.speed
                self.rect.center = self.pos

# --- 3. 실행부 ---

player = Survivor()
all_sprites = pygame.sprite.Group(player)
zombies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

try:
    font = pygame.font.SysFont("arial", 24, bold=True)
except:
    font = pygame.font.Font(None, 32)

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == SPAWN_EVENT and len(zombies) < 15:
            z = Zombie(player); zombies.add(z); all_sprites.add(z)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.weapon_mode = "GLOCK" if player.weapon_mode == "BAT" else "BAT"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.hp > 0:
            now = pygame.time.get_ticks()
            if player.weapon_mode == "GLOCK" and player.ammo > 0 and now - player.last_shot > 400:
                b = Bullet(player.rect.centerx, player.rect.centery, event.pos)
                bullets.add(b); all_sprites.add(b); player.ammo -= 1; player.last_shot = now
            elif player.weapon_mode == "BAT" and now - player.last_swing > 600:
                player.last_swing = now
                hb = player.rect.inflate(40, 40)
                for z in zombies:
                    if hb.colliderect(z.rect): z.kill()

    if player.hp > 0:
        all_sprites.update()
        pygame.sprite.groupcollide(bullets, zombies, True, True)
        if pygame.sprite.spritecollide(player, zombies, False):
            player.hp -= 0.15

    screen.fill(BG_COLOR)
    # 격자 배경
    for i in range(0, SCREEN_WIDTH, 64): pygame.draw.line(screen, (50, 55, 50), (i, 0), (i, SCREEN_HEIGHT))
    for i in range(0, SCREEN_HEIGHT, 64): pygame.draw.line(screen, (50, 55, 50), (0, i), (SCREEN_WIDTH, i))
    
    all_sprites.draw(screen)
    
    # UI
    info = f"HP: {int(player.hp)} | WEAPON: {player.weapon_mode} | AMMO: {player.ammo}"
    screen.blit(font.render(info, True, (255, 255, 255)), (20, 20))
    if player.hp <= 0:
        screen.blit(font.render("YOU ARE DEAD", True, (255, 0, 0)), (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2))

    pygame.display.flip()
    clock.tick(FPS) # 이제 정상 작동합니다!