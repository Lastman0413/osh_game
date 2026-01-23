
import pygame
import sys
import math
import random
import time

# --- 1. 초기 설정 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Zomboid: Dynamic Survivors & Undead")
clock = pygame.time.Clock()

# 색상 및 폰트
WHITE, BLACK, RED, GRAY, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0), (40, 80, 200)
SKIN, ZOMBIE_SKIN = (235, 195, 165), (140, 160, 140)
BG_COLOR = (30, 35, 30)

try:
    font_main = pygame.font.SysFont("malgungothic", 45, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 20, bold=True)
except:
    font_main = pygame.font.SysFont("arial", 45, bold=True)
    font_ui = pygame.font.SysFont("arial", 20, bold=True)

# 게임 상태 및 데이터
STATE_TITLE, STATE_SELECT, STATE_GAME = "TITLE", "SELECT", "GAME"
current_state = STATE_TITLE
selected_job = None

JOBS = {
    "Police": {"hp": 100, "glock": 30, "shotgun": 0, "speed": 2.2, "color": BLUE, "desc": "권총 특화 (파란 제복)"},
    "Firefighter": {"hp": 150, "glock": 0, "shotgun": 0, "speed": 1.9, "color": (180, 40, 40), "desc": "강한 체력 (붉은 방화복)"},
    "Survivalist": {"hp": 80, "glock": 5, "shotgun": 10, "speed": 2.5, "color": (60, 100, 60), "desc": "샷건 보유 (녹색 전술복)"}
}

# --- 2. 애니메이션 베이스 클래스 ---

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, color, is_zombie=False):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.color = color
        self.is_zombie = is_zombie
        self.walk_count = random.random() * 10
        self.base_skin = ZOMBIE_SKIN if is_zombie else SKIN

    def draw_entity(self, is_moving, weapon_mode="NONE"):
        self.image.fill((0,0,0,0))
        cx, cy = 40, 40
        # 좀비는 더 느리고 흐느적거리는 사인파 적용
        speed_factor = 0.15 if self.is_zombie else 0.22
        swing = math.sin(self.walk_count * speed_factor) * (10 if self.is_zombie else 12) if is_moving else 0
        
        # 1. 다리 (하의)
        leg_c = (max(0, self.color[0]-40), max(0, self.color[1]-40), max(0, self.color[2]-40))
        pygame.draw.rect(self.image, leg_c, (cx-9, cy+12 + swing, 7, 14)) # 왼다리
        pygame.draw.rect(self.image, leg_c, (cx+2, cy+12 - swing, 7, 14)) # 오른다리
        
        # 2. 팔 (좀비는 앞으로 나란히 하듯 흔들림)
        arm_y = -15 if self.is_zombie else 0
        pygame.draw.rect(self.image, self.base_skin, (cx-18, cy-5 + arm_y - swing, 6, 16))
        pygame.draw.rect(self.image, self.base_skin, (cx+12, cy-5 + arm_y + swing, 6, 16))
        
        # 3. 몸통 (상의)
        pygame.draw.rect(self.image, self.color, (cx-12, cy-12, 24, 26))
        
        # 4. 머리
        pygame.draw.rect(self.image, (70, 45, 35) if not self.is_zombie else (40, 50, 40), (cx-8, cy-26, 16, 15))
        pygame.draw.rect(self.image, self.base_skin, (cx-7, cy-20, 14, 9))

        # 5. 무기 (플레이어 전용)
        if not self.is_zombie:
            if weapon_mode == "BAT": pygame.draw.line(self.image, (150,110,80), (cx+8, cy), (cx+22, cy-18), 5)
            elif weapon_mode == "GLOCK": pygame.draw.rect(self.image, (40,40,40), (cx+10, cy, 12, 6))
            elif weapon_mode == "SHOTGUN": pygame.draw.rect(self.image, (20,20,20), (cx+8, cy, 18, 8))

# --- 3. 게임 객체 클래스 ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, spread=0):
        super().__init__()
        self.image = pygame.Surface((6, 6)); self.image.fill((255, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        dir_vec = pygame.Vector2(target_pos) - self.pos
        angle = math.degrees(math.atan2(dir_vec.y, dir_vec.x)) + spread if dir_vec.length() > 0 else spread
        self.velocity = pygame.Vector2(15, 0).rotate(angle)
    def update(self):
        self.pos += self.velocity; self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

class Survivor(AnimatedSprite):
    def __init__(self, job):
        stats = JOBS[job]
        super().__init__(stats["color"])
        self.job, self.hp, self.speed = job, stats["hp"], stats["speed"]
        self.ammo_glock, self.ammo_shotgun = stats["glock"], stats["shotgun"]
        self.weapon_mode, self.is_moving, self.last_act = "BAT", False, 0
        self.rect = self.image.get_rect(center=(500, 400))
        self.pos = pygame.Vector2(self.rect.center)
        self.is_infected, self.status_msg, self.death_timer = False, "건강함", None

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        self.is_moving = False
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0:
            self.pos += move.normalize() * self.speed
            self.walk_count += 1; self.is_moving = True
        self.rect.center = self.pos
        if self.is_infected and self.death_timer and time.time() >= self.death_timer: self.hp = 0
        self.draw_entity(self.is_moving, self.weapon_mode)

class Zombie(AnimatedSprite):
    def __init__(self, target):
        job_key = random.choice(list(JOBS.keys()))
        super().__init__(JOBS[job_key]["color"], is_zombie=True)
        self.target = target
        self.rect = self.image.get_rect(center=(random.choice([-50, 1050]), random.randint(0, 800)))
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = random.uniform(0.7, 1.1)

    def update(self):
        if self.target.hp > 0:
            dir_v = (self.target.pos - self.pos)
            if dir_v.length() > 0:
                self.pos += dir_v.normalize() * self.speed
                self.walk_count += 1
            self.rect.center = self.pos
        self.draw_entity(True)

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((18, 18))
        self.image.fill((220, 200, 50) if type == 'GLOCK' else (200, 60, 60))
        self.rect = self.image.get_rect(center=(x, y))

# --- 4. 메인 루프 ---

def init_game(job):
    global player, all_sprites, zombies, bullets, items
    player = Survivor(job)
    all_sprites, zombies = pygame.sprite.Group(player), pygame.sprite.Group()
    bullets, items = pygame.sprite.Group(), pygame.sprite.Group()

SPAWN_Z = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_Z, 2500)

while True:
    screen.fill(BLACK)
    m_p = pygame.mouse.get_pos()
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if current_state == STATE_TITLE and e.type == pygame.MOUSEBUTTONDOWN: current_state = STATE_SELECT
        elif current_state == STATE_SELECT and e.type == pygame.MOUSEBUTTONDOWN:
            for i, name in enumerate(JOBS.keys()):
                if pygame.Rect(100+i*300, 300, 200, 300).collidepoint(m_p):
                    init_game(name); current_state = STATE_GAME
        elif current_state == STATE_GAME:
            if e.type == SPAWN_Z and len(zombies) < 15:
                z = Zombie(player); zombies.add(z); all_sprites.add(z)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: player.weapon_mode = "BAT"
                if e.key == pygame.K_2: player.weapon_mode = "GLOCK"
                if e.key == pygame.K_3: player.weapon_mode = "SHOTGUN"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and player.hp > 0:
                now = pygame.time.get_ticks()
                if player.weapon_mode == "GLOCK" and player.ammo_glock > 0 and now - player.last_act > 400:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p)); player.ammo_glock -= 1; player.last_act = now
                elif player.weapon_mode == "SHOTGUN" and player.ammo_shotgun > 0 and now - player.last_act > 800:
                    for a in [-15, -7, 0, 7, 15]: bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p, a))
                    player.ammo_shotgun -= 1; player.last_act = now
                elif player.weapon_mode == "BAT" and now - player.last_act > 600:
                    for z in zombies:
                        if player.rect.inflate(50,50).colliderect(z.rect):
                            z.kill()
                            if random.random() < 0.2: items.add(Item(z.rect.centerx, z.rect.centery, random.choice(['GLOCK','SHOTGUN'])))
                    player.last_act = now

    if current_state == STATE_TITLE:
        t = font_main.render("PROJECT ZOMBOID: ANIMATED", True, RED)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 200))
    elif current_state == STATE_SELECT:
        for i, (name, data) in enumerate(JOBS.items()):
            r = pygame.Rect(100+i*300, 300, 200, 300)
            pygame.draw.rect(screen, data["color"], r, 3)
            screen.blit(font_ui.render(name, True, WHITE), (r.x+10, r.y+10))
    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        if player.hp > 0:
            all_sprites.update(); bullets.update()
            pygame.sprite.groupcollide(bullets, zombies, True, True)
            for it in pygame.sprite.spritecollide(player, items, True):
                if it.type == 'GLOCK': player.ammo_glock += 15
                else: player.ammo_shotgun += 4
            if pygame.sprite.spritecollide(player, zombies, False): player.hp -= 0.1
        items.draw(screen); bullets.draw(screen); all_sprites.draw(screen)
        screen.blit(font_ui.render(f"HP: {int(player.hp)} | [1]BAT [2]Pistol:{player.ammo_glock} [3]Shotgun:{player.ammo_shotgun}", True, WHITE), (20, 20))

    pygame.display.flip()
    clock.tick(FPS)