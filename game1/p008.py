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
pygame.display.set_caption("Zomboid Clone: The Last Minute")
clock = pygame.time.Clock()

# 색상 및 폰트
WHITE, BLACK, RED, GRAY, GREEN = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0)
BG_COLOR = (35, 40, 35)
SKIN, HAIR, TOP, PANTS = (235, 195, 165), (80, 50, 40), (70, 80, 60), (50, 55, 70)
ZOMBIE_SKIN = (140, 160, 140)

try:
    font_main = pygame.font.SysFont("malgungothic", 40, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 22, bold=True)
except:
    font_main = pygame.font.SysFont("arial", 40, bold=True)
    font_ui = pygame.font.SysFont("arial", 22, bold=True)

# 게임 상태
STATE_TITLE = "TITLE"
STATE_PROLOGUE = "PROLOGUE"
STATE_GAME = "GAME"
current_state = STATE_TITLE

# --- 2. 핵심 클래스 정의 ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.image = pygame.Surface((8, 8)); self.image.fill((255, 220, 100))
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
        
        # 부상 시스템
        self.is_infected = False
        self.status_msg = "건강함"
        self.death_timer = None
        self.last_damage_time = 0

    def check_injury(self):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time < 1200: return # 1.2초 무적

        rand = random.random() * 100
        if rand <= 0.05: # 물림
            self.status_msg = "물림 (감염됨)"
            self.trigger_infection()
        elif rand <= 20.05: # 찢어진 상처
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
            self.is_infected = True
            self.death_timer = time.time() + 60 # 60초 카운트다운

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0: self.pos += move.normalize() * 2.1
        self.rect.center = self.pos
        self.rect.clamp_ip(screen.get_rect())

        if self.is_infected and self.death_timer:
            if time.time() >= self.death_timer: self.hp = 0
        if self.hp <= 0: self.hp = 0; self.status_msg = "사망함"
        self.draw_player()

    def draw_player(self):
        self.image.fill((0,0,0,0))
        face_color = (180, 200, 180) if self.is_infected else SKIN
        pygame.draw.rect(self.image, HAIR, (24, 8, 16, 16))
        pygame.draw.rect(self.image, face_color, (26, 16, 12, 8))
        pygame.draw.rect(self.image, TOP, (20, 24, 24, 24))
        pygame.draw.rect(self.image, PANTS, (20, 48, 24, 12))
        if self.weapon_mode == "BAT": pygame.draw.line(self.image, (150,110,80), (32,32), (56,16), 6)
        else: pygame.draw.rect(self.image, (50,50,50), (40,32,16,8))

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
            dir_vec = self.target.pos - self.pos
            if dir_vec.length() > 0: self.pos += dir_vec.normalize() * 0.75
            self.rect.center = self.pos

# --- 3. UI 및 환경 요소 ---

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

class EnvDetail:
    def __init__(self):
        self.pos = (random.randint(0, 1000), random.randint(0, 800))
        self.type = random.choice(['BLOOD', 'GRASS'])
        self.size = random.randint(15, 30)
    def draw(self, surf):
        color = (100, 0, 0) if self.type == 'BLOOD' else (50, 60, 45)
        if self.type == 'BLOOD': pygame.draw.ellipse(surf, color, (self.pos[0], self.pos[1], self.size*1.5, self.size))
        else: pygame.draw.rect(surf, color, (self.pos[0], self.pos[1], self.size, self.size//2))

# --- 4. 메인 변수 및 초기화 ---

btn_new = Button("새 게임", 400, 350, 200, 50)
btn_exit = Button("나가기", 400, 420, 200, 50)
prologue_lines = ["세상은 단 며칠 만에 무너졌다.", "이것은 당신이 어떻게 죽었는지에 대한 기록이다."]
pro_idx = 0

def init_game():
    global player, all_sprites, zombies, bullets, details
    player = Survivor()
    all_sprites = pygame.sprite.Group(player)
    zombies, bullets = pygame.sprite.Group(), pygame.sprite.Group()
    details = [EnvDetail() for _ in range(40)]

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2500)

# --- 5. 게임 루프 ---

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
            if event.type == SPAWN_EVENT and len(zombies) < 12:
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
                    for z in zombies:
                        if player.rect.inflate(40,40).colliderect(z.rect): z.kill()

    # --- 렌더링 영역 ---
    if current_state == STATE_TITLE:
        title = font_main.render("PROJECT ZOMBOID CLONE", True, RED)
        screen.blit(title, (500 - title.get_width()//2, 200))
        btn_new.draw(screen); btn_exit.draw(screen)
        
    elif current_state == STATE_PROLOGUE:
        txt = font_ui.render(prologue_lines[pro_idx], True, WHITE)
        screen.blit(txt, (500 - txt.get_width()//2, 380))
        tip = font_ui.render("[ SPACE ] 키를 눌러 진행", True, (80,80,80))
        screen.blit(tip, (500 - tip.get_width()//2, 700))
        
    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        for d in details: d.draw(screen)
        
        if player.hp > 0:
            all_sprites.update()
            pygame.sprite.groupcollide(bullets, zombies, True, True)
            if pygame.sprite.spritecollide(player, zombies, False): player.check_injury()
        
        all_sprites.draw(screen)
        
        # UI 레이어
        hp_col = RED if player.is_infected else GREEN
        hp_bar = font_ui.render(f"상태: {player.status_msg} | HP: {int(player.hp)}", True, hp_col)
        screen.blit(hp_bar, (20, 20))
        
        if player.weapon_mode == "GLOCK":
            ammo_txt = font_ui.render(f"탄약: {player.ammo}/17", True, (255,200,0))
            screen.blit(ammo_txt, (20, 50))

        if player.is_infected and player.hp > 0:
            rem = max(0, int(player.death_timer - time.time()))
            timer_txt = font_ui.render(f"남은 시간: {rem}초", True, RED)
            screen.blit(timer_txt, (SCREEN_WIDTH - 150, 20))

        if player.hp <= 0:
            over = font_main.render("YOU DIED", True, RED)
            screen.blit(over, (500 - over.get_width()//2, 350))

    pygame.display.flip()
    clock.tick(FPS)