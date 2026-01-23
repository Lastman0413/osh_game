
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
pygame.display.set_caption("Project Zomboid: Professional Survivors")
clock = pygame.time.Clock()

# 색상 및 폰트
WHITE, BLACK, RED, GRAY, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0), (50, 100, 255)
BG_COLOR = (35, 40, 35)

try:
    font_main = pygame.font.SysFont("malgungothic", 45, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 20, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 16)
except:
    font_main = pygame.font.SysFont("arial", 45, bold=True)
    font_ui = pygame.font.SysFont("arial", 20, bold=True)
    font_small = pygame.font.SysFont("arial", 16)

# 게임 상태 및 직업 데이터
STATE_TITLE, STATE_SELECT, STATE_PROLOGUE, STATE_GAME = "TITLE", "SELECT", "PROLOGUE", "GAME"
current_state = STATE_TITLE
selected_job = None

JOBS = {
    "Police": {"hp": 100, "glock": 30, "shotgun": 0, "speed": 2.2, "color": BLUE, "desc": "권총 탄약 특화"},
    "Firefighter": {"hp": 150, "glock": 0, "shotgun": 0, "speed": 1.9, "color": (200, 80, 0), "desc": "높은 체력, 근접 생존"},
    "Survivalist": {"hp": 80, "glock": 5, "shotgun": 10, "speed": 2.5, "color": (70, 90, 70), "desc": "샷건 보유, 빠른 이동"}
}

# --- 2. 게임 클래스 (Bullet, Item, Zombie 동일) ---

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.type = item_type
        self.image = pygame.Surface((20, 20))
        self.image.fill((200, 200, 100) if item_type == 'AMMO_GLOCK' else (200, 50, 50))
        pygame.draw.rect(self.image, WHITE, (0,0,20,20), 1)
        self.rect = self.image.get_rect(center=(x, y))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, spread_angle=0):
        super().__init__()
        self.image = pygame.Surface((6, 6)); self.image.fill((255, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        direction = pygame.Vector2(target_pos) - self.pos
        if direction.length() > 0:
            angle = math.degrees(math.atan2(direction.y, direction.x)) + spread_angle
            rad = math.radians(angle)
            self.velocity = pygame.Vector2(math.cos(rad), math.sin(rad)) * 15
        else: self.velocity = pygame.Vector2(1, 0) * 15
    def update(self):
        self.pos += self.velocity; self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self, job_name):
        super().__init__()
        stats = JOBS[job_name]
        self.job = job_name
        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.ammo_glock = stats["glock"]
        self.ammo_shotgun = stats["shotgun"]
        self.speed = stats["speed"]
        self.weapon_mode = "BAT"
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(500, 400))
        self.pos = pygame.Vector2(self.rect.center)
        self.is_infected, self.status_msg, self.death_timer, self.last_damage = False, "건강함", None, 0
        self.last_action = 0

    def check_injury(self):
        now = pygame.time.get_ticks()
        if now - self.last_damage < 1200: return
        rand = random.random() * 100
        if rand <= 0.05: self.status_msg = "물림 (감염됨)"; self.trigger_infection()
        elif rand <= 20.05: self.hp -= 15; self.status_msg = "찢어진 상처"; (self.trigger_infection() if random.random() < 0.10 else None)
        elif rand <= 70.05: self.hp -= 5; self.status_msg = "긁힘"; (self.trigger_infection() if random.random() < 0.03 else None)
        self.last_damage = now

    def trigger_infection(self):
        if not self.is_infected: self.is_infected, self.death_timer = True, time.time() + 60

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0: self.pos += move.normalize() * self.speed
        self.rect.center = self.pos
        if self.is_infected and self.death_timer and time.time() >= self.death_timer: self.hp = 0
        if self.hp <= 0: self.hp = 0; self.status_msg = "사망함"
        self.draw_player()

    def draw_player(self):
        self.image.fill((0,0,0,0))
        c = (180, 200, 180) if self.is_infected else (235, 195, 165)
        pygame.draw.rect(self.image, (80, 50, 40), (24, 8, 16, 16)) # 머리
        pygame.draw.rect(self.image, c, (26, 16, 12, 8)) # 얼굴
        pygame.draw.rect(self.image, JOBS[self.job]["color"], (20, 24, 24, 24)) # 직업별 옷
        if self.weapon_mode == "BAT": pygame.draw.line(self.image, (150,110,80), (32,32), (56,16), 6)
        elif self.weapon_mode == "GLOCK": pygame.draw.rect(self.image, (50,50,50), (40,32,14,7))
        elif self.weapon_mode == "SHOTGUN": pygame.draw.rect(self.image, (30,30,30), (35,30,25,9))

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 70, 60), (24, 12, 16, 16))
        pygame.draw.rect(self.image, (140, 160, 140), (20, 28, 24, 28))
        self.rect = self.image.get_rect(center=(random.choice([-50, 1050]), random.randint(0, 800)))
        self.pos = pygame.Vector2(self.rect.center)
    def update(self):
        if self.target.hp > 0:
            dir = (self.target.pos - self.pos)
            if dir.length() > 0: self.pos += dir.normalize() * 0.8
            self.rect.center = self.pos

# --- 3. 게임 실행 함수 및 변수 ---

def init_game(job_name):
    global player, all_sprites, zombies, bullets, items
    player = Survivor(job_name)
    all_sprites = pygame.sprite.Group(player)
    zombies, bullets, items = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    for _ in range(5):
        items.add(Item(random.randint(100, 900), random.randint(100, 700), random.choice(['AMMO_GLOCK', 'AMMO_SHOTGUN'])))

SPAWN_ZOMBIE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ZOMBIE, 2500)

prologue_lines = ["세상은 단 며칠 만에 무너졌다.", "이것은 당신이 어떻게 죽었는지에 대한 기록이다."]
pro_idx = 0

# --- 4. 메인 루프 ---

while True:
    screen.fill(BLACK)
    events = pygame.event.get()
    m_pos = pygame.mouse.get_pos()
    
    for event in events:
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if current_state == STATE_TITLE:
            if event.type == pygame.MOUSEBUTTONDOWN: current_state = STATE_SELECT
            
        elif current_state == STATE_SELECT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, name in enumerate(JOBS.keys()):
                    rect = pygame.Rect(100 + i*300, 300, 200, 300)
                    if rect.collidepoint(m_pos):
                        selected_job = name
                        current_state = STATE_PROLOGUE
        
        elif current_state == STATE_PROLOGUE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pro_idx += 1
                if pro_idx >= len(prologue_lines): init_game(selected_job); current_state = STATE_GAME

        elif current_state == STATE_GAME:
            if event.type == SPAWN_ZOMBIE and len(zombies) < 15:
                z = Zombie(player); zombies.add(z); all_sprites.add(z)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: player.weapon_mode = "BAT"
                if event.key == pygame.K_2: player.weapon_mode = "GLOCK"
                if event.key == pygame.K_3: player.weapon_mode = "SHOTGUN"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.hp > 0:
                now = pygame.time.get_ticks()
                if player.weapon_mode == "GLOCK" and player.ammo_glock > 0 and now - player.last_action > 400:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_pos)); player.ammo_glock -= 1; player.last_action = now
                elif player.weapon_mode == "SHOTGUN" and player.ammo_shotgun > 0 and now - player.last_action > 800:
                    for angle in [-15, -7, 0, 7, 15]: bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_pos, angle))
                    player.ammo_shotgun -= 1; player.last_action = now
                elif player.weapon_mode == "BAT" and now - player.last_action > 600:
                    for z in zombies:
                        if player.rect.inflate(50,50).colliderect(z.rect):
                            z.kill()
                            if random.random() < 0.2: items.add(Item(z.rect.centerx, z.rect.centery, random.choice(['AMMO_GLOCK', 'AMMO_SHOTGUN'])))
                    player.last_action = now

    # --- 렌더링 영역 ---
    if current_state == STATE_TITLE:
        t = font_main.render("PROJECT ZOMBOID CLONE", True, RED)
        screen.blit(t, (500 - t.get_width()//2, 200))
        screen.blit(font_ui.render("클릭하여 시작", True, WHITE), (440, 500))

    elif current_state == STATE_SELECT:
        screen.blit(font_main.render("직업을 선택하십시오", True, WHITE), (320, 150))
        for i, (name, data) in enumerate(JOBS.items()):
            rect = pygame.Rect(100 + i*300, 300, 200, 300)
            color = (80, 80, 80) if rect.collidepoint(m_pos) else GRAY
            pygame.draw.rect(screen, color, rect); pygame.draw.rect(screen, WHITE, rect, 2)
            screen.blit(font_ui.render(name, True, WHITE), (rect.x+10, rect.y+10))
            screen.blit(font_small.render(data["desc"], True, GREEN), (rect.x+10, rect.y+50))
            screen.blit(font_small.render(f"HP: {data['hp']}", True, WHITE), (rect.x+10, rect.y+240))
            screen.blit(font_small.render(f"SPEED: {data['speed']}", True, WHITE), (rect.x+10, rect.y+265))

    elif current_state == STATE_PROLOGUE:
        p_txt = font_ui.render(prologue_lines[pro_idx], True, WHITE)
        screen.blit(p_txt, (500 - p_txt.get_width()//2, 380))
        screen.blit(font_ui.render("[ SPACE ] 키로 진행", True, (100,100,100)), (440, 700))

    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        if player.hp > 0:
            all_sprites.update(); bullets.update()
            if pygame.sprite.spritecollide(player, zombies, False): player.check_injury()
            pygame.sprite.groupcollide(bullets, zombies, True, True)
            for item in pygame.sprite.spritecollide(player, items, True):
                if item.type == 'AMMO_GLOCK': player.ammo_glock += 15
                else: player.ammo_shotgun += 4
        items.draw(screen); bullets.draw(screen); all_sprites.draw(screen)
        
        # UI
        hp_col = RED if player.is_infected else GREEN
        screen.blit(font_ui.render(f"{player.job} | {player.status_msg} | HP: {int(player.hp)}", True, hp_col), (20, 20))
        screen.blit(font_ui.render(f"[1]방망이 [2]권총:{player.ammo_glock} [3]샷건:{player.ammo_shotgun}", True, WHITE), (20, 50))
        if player.is_infected and player.hp > 0:
            screen.blit(font_ui.render(f"남은 시간: {max(0, int(player.death_timer - time.time()))}s", True, RED), (850, 20))
        if player.hp <= 0: screen.blit(font_main.render("YOU DIED", True, RED), (400, 350))

    pygame.display.flip()
    clock.tick(FPS)