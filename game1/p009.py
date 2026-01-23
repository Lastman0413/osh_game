import pygame
import sys
import math
import random
import time

# --- 1. 초기 설정 및 환경 변수 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Zomboid: Scavenger's Fate")
clock = pygame.time.Clock()

# 색상 정의
WHITE, BLACK, RED, GRAY, GREEN = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0)
BG_COLOR = (35, 40, 35)
AMMO_GLOCK_COLOR = (200, 200, 100)
AMMO_SHOTGUN_COLOR = (200, 50, 50)
ZOMBIE_SKIN = (140, 160, 140)

# 폰트 로드
try:
    font_main = pygame.font.SysFont("malgungothic", 45, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 20, bold=True)
except:
    font_main = pygame.font.SysFont("arial", 45, bold=True)
    font_ui = pygame.font.SysFont("arial", 20, bold=True)

# 게임 상태 관리
STATE_TITLE, STATE_PROLOGUE, STATE_GAME = "TITLE", "PROLOGUE", "GAME"
current_state = STATE_TITLE

# --- 2. 클래스 정의 ---

class Item(pygame.sprite.Sprite):
    """맵에 떨어지는 탄약 아이템"""
    def __init__(self, x, y, item_type):
        super().__init__()
        self.type = item_type # 'AMMO_GLOCK' 또는 'AMMO_SHOTGUN'
        self.image = pygame.Surface((20, 20))
        self.image.fill(AMMO_GLOCK_COLOR if item_type == 'AMMO_GLOCK' else AMMO_SHOTGUN_COLOR)
        pygame.draw.rect(self.image, WHITE, (0, 0, 20, 20), 1)
        self.rect = self.image.get_rect(center=(x, y))

class Bullet(pygame.sprite.Sprite):
    """권총 및 샷건 탄환"""
    def __init__(self, x, y, target_pos, spread_angle=0):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill((255, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        
        direction = pygame.Vector2(target_pos) - self.pos
        if direction.length() > 0:
            angle = math.degrees(math.atan2(direction.y, direction.x)) + spread_angle
            rad = math.radians(angle)
            self.velocity = pygame.Vector2(math.cos(rad), math.sin(rad)) * 15
        else:
            self.velocity = pygame.Vector2(1, 0) * 15

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect):
            self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hp, self.ammo_glock, self.ammo_shotgun = 100, 15, 5
        self.weapon_mode = "BAT" # BAT, GLOCK, SHOTGUN
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(500, 400))
        self.pos = pygame.Vector2(self.rect.center)
        self.last_action = 0
        # 부상 시스템
        self.is_infected = False
        self.status_msg = "건강함"
        self.death_timer = None
        self.last_damage_time = 0

    def check_injury(self):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time < 1200: return # 무적 시간

        rand = random.random() * 100
        if rand <= 0.05: # 물림
            self.status_msg = "물림 (감염됨)"
            self.trigger_infection()
        elif rand <= 20.05: # 찢어짐
            self.hp -= 15
            self.status_msg = "찢어진 상처"
            if random.random() < 0.10: self.trigger_infection()
        elif rand <= 70.05: # 긁힘
            self.hp -= 5
            self.status_msg = "긁힘"
            if random.random() < 0.03: self.trigger_infection()
        self.last_damage_time = now

    def trigger_infection(self):
        if not self.is_infected:
            self.is_infected, self.death_timer = True, time.time() + 60

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0: self.pos += move.normalize() * 2.3
        self.rect.center = self.pos
        self.rect.clamp_ip(screen.get_rect())
        
        if self.is_infected and self.death_timer and time.time() >= self.death_timer:
            self.hp = 0
        if self.hp <= 0: self.hp, self.status_msg = 0, "사망함"
        self.draw_player()

    def draw_player(self):
        self.image.fill((0,0,0,0))
        c = (180, 200, 180) if self.is_infected else (235, 195, 165)
        pygame.draw.rect(self.image, (80, 50, 40), (24, 8, 16, 16)) # 머리
        pygame.draw.rect(self.image, c, (26, 16, 12, 8)) # 얼굴
        pygame.draw.rect(self.image, (70, 80, 60), (20, 24, 24, 24)) # 몸
        if self.weapon_mode == "BAT": pygame.draw.line(self.image, (150,110,80), (32,32), (56,16), 6)
        elif self.weapon_mode == "GLOCK": pygame.draw.rect(self.image, (50,50,50), (40,32,14,7))
        elif self.weapon_mode == "SHOTGUN": pygame.draw.rect(self.image, (30,30,30), (35,30,25,9))

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 70, 60), (24, 12, 16, 16))
        pygame.draw.rect(self.image, ZOMBIE_SKIN, (20, 28, 24, 28))
        side = random.choice(['T','B','L','R'])
        if side=='T': x,y = random.randint(0,1000), -50
        elif side=='B': x,y = random.randint(0,1000), 850
        else: x,y = (-50 if side=='L' else 1050), random.randint(0,800)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)

    def update(self):
        if self.target.hp > 0:
            dir = (self.target.pos - self.pos)
            if dir.length() > 0: self.pos += dir.normalize() * 0.8
            self.rect.center = self.pos

# --- 3. GUI 및 환경 ---

class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h); self.text = text
    def draw(self, surf):
        m_pos = pygame.mouse.get_pos()
        color = (100, 100, 100) if self.rect.collidepoint(m_pos) else GRAY
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, WHITE, self.rect, 2)
        txt = font_ui.render(self.text, True, WHITE)
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

btn_new = Button("새 게임", 400, 350, 200, 50)
btn_exit = Button("나가기", 400, 420, 200, 50)
prologue_lines = ["세상은 단 며칠 만에 무너졌다.", "이것은 당신이 어떻게 죽었는지에 대한 기록이다."]
pro_idx = 0

def init_game():
    global player, all_sprites, zombies, bullets, items
    player = Survivor()
    all_sprites = pygame.sprite.Group(player)
    zombies, bullets, items = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    for _ in range(5): # 초기 아이템 스폰
        items.add(Item(random.randint(100, 900), random.randint(100, 700), random.choice(['AMMO_GLOCK', 'AMMO_SHOTGUN'])))

SPAWN_ZOMBIE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ZOMBIE, 2500)

# --- 4. 메인 루프 ---

while True:
    screen.fill(BLACK)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if current_state == STATE_TITLE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_new.rect.collidepoint(event.pos): current_state = STATE_PROLOGUE
                if btn_exit.rect.collidepoint(event.pos): pygame.quit(); sys.exit()
        
        elif current_state == STATE_PROLOGUE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pro_idx += 1
                if pro_idx >= len(prologue_lines): init_game(); current_state = STATE_GAME
        
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
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, event.pos))
                    player.ammo_glock -= 1; player.last_action = now
                elif player.weapon_mode == "SHOTGUN" and player.ammo_shotgun > 0 and now - player.last_action > 800:
                    for angle in [-15, -7, 0, 7, 15]: # 5발 확산
                        bullets.add(Bullet(player.rect.centerx, player.rect.centery, event.pos, angle))
                    player.ammo_shotgun -= 1; player.last_action = now
                elif player.weapon_mode == "BAT" and now - player.last_action > 600:
                    for z in zombies:
                        if player.rect.inflate(50, 50).colliderect(z.rect):
                            z.kill()
                            if random.random() < 0.2: # 20% 확률로 아이템 드랍
                                items.add(Item(z.rect.centerx, z.rect.centery, random.choice(['AMMO_GLOCK', 'AMMO_SHOTGUN'])))
                    player.last_action = now

    # --- 그리기 및 업데이트 ---
    if current_state == STATE_TITLE:
        t = font_main.render("PROJECT ZOMBOID CLONE", True, RED)
        screen.blit(t, (500 - t.get_width()//2, 200))
        btn_new.draw(screen); btn_exit.draw(screen)
        
    elif current_state == STATE_PROLOGUE:
        p_txt = font_ui.render(prologue_lines[pro_idx], True, WHITE)
        screen.blit(p_txt, (500 - p_txt.get_width()//2, 380))
        screen.blit(font_ui.render("[ SPACE ] 키로 진행", True, (100,100,100)), (440, 700))
        
    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        if player.hp > 0:
            all_sprites.update()
            bullets.update()
            # 아이템 습득 및 충돌
            if pygame.sprite.spritecollide(player, zombies, False): player.check_injury()
            pygame.sprite.groupcollide(bullets, zombies, True, True)
            for item in pygame.sprite.spritecollide(player, items, True):
                if item.type == 'AMMO_GLOCK': player.ammo_glock += 15
                else: player.ammo_shotgun += 4

        items.draw(screen); bullets.draw(screen); all_sprites.draw(screen)
        
        # UI 레이어
        hp_col = RED if player.is_infected else GREEN
        ui_texts = [
            f"상태: {player.status_msg} | HP: {int(player.hp)}",
            f"[1]방망이 [2]권총:{player.ammo_glock} [3]샷건:{player.ammo_shotgun}",
            f"사망까지: {max(0, int(player.death_timer - time.time()))}s" if player.is_infected else ""
        ]
        for i, text in enumerate(ui_texts):
            screen.blit(font_ui.render(text, True, WHITE if i != 0 else hp_col), (20, 20 + i*30))
        
        if player.hp <= 0:
            over = font_main.render("YOU DIED", True, RED)
            screen.blit(over, (500 - over.get_width()//2, 350))

    pygame.display.flip()
    clock.tick(FPS)