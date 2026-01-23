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
pygame.display.set_caption("Project Zomboid: Animated Survivors")
clock = pygame.time.Clock()

# 색상 정의
WHITE, BLACK, RED, GRAY, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0), (40, 80, 200)
SKIN = (235, 195, 165)
BG_COLOR = (30, 35, 30)

# 폰트 로드
try:
    font_main = pygame.font.SysFont("malgungothic", 40, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 20, bold=True)
except:
    font_main = pygame.font.SysFont("arial", 40, bold=True)
    font_ui = pygame.font.SysFont("arial", 20, bold=True)

# 게임 상태 및 직업 데이터
STATE_TITLE, STATE_SELECT, STATE_GAME = "TITLE", "SELECT", "GAME"
current_state = STATE_TITLE
selected_job = None

JOBS = {
    "Police": {"hp": 100, "glock": 30, "shotgun": 0, "speed": 2.2, "color": BLUE, "desc": "권총 특화 (파란 제복)"},
    "Firefighter": {"hp": 150, "glock": 0, "shotgun": 0, "speed": 1.9, "color": (180, 40, 40), "desc": "강한 체력 (붉은 방화복)"},
    "Survivalist": {"hp": 80, "glock": 5, "shotgun": 10, "speed": 2.5, "color": (60, 100, 60), "desc": "샷건 보유 (녹색 전술복)"}
}

# --- 2. 클래스 정의 ---

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.type = item_type
        self.image = pygame.Surface((18, 18))
        self.image.fill((220, 200, 50) if item_type == 'AMMO_GLOCK' else (200, 60, 60))
        pygame.draw.rect(self.image, WHITE, (0,0,18,18), 1)
        self.rect = self.image.get_rect(center=(x, y))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, spread_angle=0):
        super().__init__()
        self.image = pygame.Surface((6, 6)); self.image.fill((255, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        dir_vec = pygame.Vector2(target_pos) - self.pos
        if dir_vec.length() > 0:
            angle = math.degrees(math.atan2(dir_vec.y, dir_vec.x)) + spread_angle
            self.velocity = pygame.Vector2(1, 0).rotate(angle) * 15
        else: self.velocity = pygame.Vector2(15, 0)
    def update(self):
        self.pos += self.velocity; self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self, job_name):
        super().__init__()
        stats = JOBS[job_name]
        self.job, self.hp, self.speed = job_name, stats["hp"], stats["speed"]
        self.ammo_glock, self.ammo_shotgun, self.color = stats["glock"], stats["shotgun"], stats["color"]
        self.weapon_mode = "BAT"
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(500, 400))
        self.pos = pygame.Vector2(self.rect.center)
        # 애니메이션/상태 변수
        self.walk_count, self.is_moving = 0, False
        self.is_infected, self.status_msg, self.death_timer, self.last_dmg = False, "건강함", None, 0
        self.last_action = 0

    def check_injury(self):
        now = pygame.time.get_ticks()
        if now - self.last_dmg < 1200: return
        r = random.random() * 100
        if r <= 0.05: self.status_msg = "물림 (감염됨)"; self.trigger_infection()
        elif r <= 20.05: self.hp -= 15; self.status_msg = "찢어진 상처"; (self.trigger_infection() if random.random() < 0.10 else None)
        elif r <= 70.05: self.hp -= 5; self.status_msg = "긁힘"; (self.trigger_infection() if random.random() < 0.03 else None)
        self.last_dmg = now

    def trigger_infection(self):
        if not self.is_infected: self.is_infected, self.death_timer = True, time.time() + 60

    def draw_player(self):
        self.image.fill((0,0,0,0))
        cx, cy = 40, 40
        swing = math.sin(self.walk_count * 0.2) * 12 if self.is_moving else 0
        
        # 다리
        leg_c = (max(0, self.color[0]-40), max(0, self.color[1]-40), max(0, self.color[2]-40))
        pygame.draw.rect(self.image, leg_c, (cx-10, cy+12 + swing, 7, 14)) # 왼
        pygame.draw.rect(self.image, leg_c, (cx+3, cy+12 - swing, 7, 14))  # 오
        # 팔
        pygame.draw.rect(self.image, SKIN, (cx-18, cy-5 - swing, 6, 16)) # 왼
        pygame.draw.rect(self.image, SKIN, (cx+12, cy-5 + swing, 6, 16)) # 오
        # 몸통
        pygame.draw.rect(self.image, self.color, (cx-12, cy-12, 24, 26))
        # 머리
        h_c = (180, 200, 180) if self.is_infected else SKIN
        pygame.draw.rect(self.image, (70, 45, 35), (cx-8, cy-26, 16, 15)) # 머리카락
        pygame.draw.rect(self.image, h_c, (cx-7, cy-20, 14, 9)) # 얼굴
        
        # 무기
        if self.weapon_mode == "BAT": pygame.draw.line(self.image, (150,110,80), (cx+8, cy), (cx+22, cy-18), 5)
        elif self.weapon_mode == "GLOCK": pygame.draw.rect(self.image, (40,40,40), (cx+10, cy, 12, 6))
        elif self.weapon_mode == "SHOTGUN": pygame.draw.rect(self.image, (20,20,20), (cx+8, cy, 18, 8))

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
        self.draw_player()

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 70, 60), (24, 12, 16, 16))
        pygame.draw.rect(self.image, (130, 150, 130), (20, 28, 24, 28))
        side = random.choice(['T','B','L','R'])
        if side=='T': x,y = random.randint(0,1000), -50
        elif side=='B': x,y = random.randint(0,1000), 850
        else: x,y = (-50 if side=='L' else 1050), random.randint(0,800)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
    def update(self):
        if self.target.hp > 0:
            dir = (self.target.pos - self.pos)
            if dir.length() > 0: self.pos += dir.normalize() * 0.85
            self.rect.center = self.pos

# --- 3. 메인 게임 루프 ---

def init_game(job):
    global player, all_sprites, zombies, bullets, items
    player = Survivor(job)
    all_sprites, zombies = pygame.sprite.Group(player), pygame.sprite.Group()
    bullets, items = pygame.sprite.Group(), pygame.sprite.Group()

SPAWN_Z = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_Z, 2500)

while True:
    screen.fill(BLACK)
    evs = pygame.event.get()
    m_p = pygame.mouse.get_pos()
    
    for e in evs:
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if current_state == STATE_TITLE:
            if e.type == pygame.MOUSEBUTTONDOWN: current_state = STATE_SELECT
        elif current_state == STATE_SELECT:
            if e.type == pygame.MOUSEBUTTONDOWN:
                for i, name in enumerate(JOBS.keys()):
                    if pygame.Rect(100 + i*300, 300, 200, 300).collidepoint(m_p):
                        selected_job = name; init_game(name); current_state = STATE_GAME
        elif current_state == STATE_GAME:
            if e.type == SPAWN_Z and len(zombies) < 15:
                z = Zombie(player); zombies.add(z); all_sprites.add(z)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: player.weapon_mode = "BAT"
                if e.key == pygame.K_2: player.weapon_mode = "GLOCK"
                if e.key == pygame.K_3: player.weapon_mode = "SHOTGUN"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and player.hp > 0:
                now = pygame.time.get_ticks()
                if player.weapon_mode == "GLOCK" and player.ammo_glock > 0 and now - player.last_action > 400:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p)); player.ammo_glock -= 1; player.last_action = now
                elif player.weapon_mode == "SHOTGUN" and player.ammo_shotgun > 0 and now - player.last_action > 800:
                    for a in [-15, -7, 0, 7, 15]: bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p, a))
                    player.ammo_shotgun -= 1; player.last_action = now
                elif player.weapon_mode == "BAT" and now - player.last_action > 600:
                    for z in zombies:
                        if player.rect.inflate(50,50).colliderect(z.rect):
                            z.kill()
                            if random.random() < 0.2: items.add(Item(z.rect.centerx, z.rect.centery, random.choice(['AMMO_GLOCK','AMMO_SHOTGUN'])))
                    player.last_action = now

    if current_state == STATE_TITLE:
        txt = font_main.render("PROJECT ZOMBOID: REBIRTH", True, RED)
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 200))
        screen.blit(font_ui.render("클릭하여 시작", True, WHITE), (440, 500))
    elif current_state == STATE_SELECT:
        for i, (name, data) in enumerate(JOBS.items()):
            r = pygame.Rect(100 + i*300, 300, 200, 300)
            pygame.draw.rect(screen, GRAY if r.collidepoint(m_p) else (30,30,30), r)
            pygame.draw.rect(screen, data["color"], r, 3)
            screen.blit(font_ui.render(name, True, WHITE), (r.x+10, r.y+10))
            screen.blit(font_ui.render(data["desc"], True, WHITE), (r.x+10, r.y+50))
    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        if player.hp > 0:
            all_sprites.update(); bullets.update()
            if pygame.sprite.spritecollide(player, zombies, False): player.check_injury()
            pygame.sprite.groupcollide(bullets, zombies, True, True)
            for it in pygame.sprite.spritecollide(player, items, True):
                if it.type == 'AMMO_GLOCK': player.ammo_glock += 15
                else: player.ammo_shotgun += 4
        items.draw(screen); bullets.draw(screen); all_sprites.draw(screen)
        
        # UI
        hp_c = RED if player.is_infected else GREEN
        screen.blit(font_ui.render(f"{player.job} | {player.status_msg} | HP: {int(player.hp)}", True, hp_c), (20, 20))
        screen.blit(font_ui.render(f"[1]방망이 [2]권총:{player.ammo_glock} [3]샷건:{player.ammo_shotgun}", True, WHITE), (20, 50))
        if player.is_infected and player.hp > 0:
            screen.blit(font_ui.render(f"감염 사망까지: {max(0, int(player.death_timer - time.time()))}s", True, RED), (750, 20))
        if player.hp <= 0:
            msg = font_main.render("당신은 좀비가 되었습니다", True, RED)
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 350))

    pygame.display.flip()
    clock.tick(FPS)