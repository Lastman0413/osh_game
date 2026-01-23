import pygame
import sys
import math
import random

# --- 1. 환경 설정 및 상숫값 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
CHAR_SIZE = 64
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Zomboid Clone - Integrated")
clock = pygame.time.Clock()

# 색상 및 폰트
WHITE, BLACK, RED, GRAY = (255, 255, 255), (0, 0, 0), (150, 0, 0), (50, 50, 50)
BG_COLOR = (35, 40, 35)
SKIN, HAIR, TOP, PANTS = (235, 195, 165), (80, 50, 40), (70, 80, 60), (50, 55, 70)
ZOMBIE_SKIN = (140, 160, 140)

try:
    font_title = pygame.font.SysFont("malgungothic", 50, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 25, bold=True)
except:
    font_title = pygame.font.SysFont("arial", 50, bold=True)
    font_ui = pygame.font.SysFont("arial", 25, bold=True)

# 게임 상태 정의
STATE_TITLE = "TITLE"
STATE_PROLOGUE = "PROLOGUE"
STATE_GAME = "GAME"
current_state = STATE_TITLE

# --- 2. 게임 객체 클래스 (Survivor, Zombie, Bullet) ---

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
        self.image = pygame.Surface((CHAR_SIZE, CHAR_SIZE), pygame.SRCALPHA)
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
        self.rect.clamp_ip(screen.get_rect())
        self.draw_player()
    def draw_player(self):
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
        self.image = pygame.Surface((CHAR_SIZE, CHAR_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 70, 60), (24, 12, 16, 16))
        pygame.draw.rect(self.image, ZOMBIE_SKIN, (20, 28, 24, 28))
        side = random.choice(['T','B','L','R'])
        if side=='T': x,y = random.randint(0,1000), -50
        elif side=='B': x,y = random.randint(0,1000), 850
        else: x,y = (-50 if side=='L' else 1050), random.randint(0,800)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
    def update(self):
        dir_vec = self.target.pos - self.pos
        if dir_vec.length() > 0: self.pos += dir_vec.normalize() * 0.8
        self.rect.center = self.pos

# --- 3. GUI 클래스 및 데이터 ---

class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
    def draw(self, surf):
        mouse_pos = pygame.mouse.get_pos()
        color = (80, 80, 80) if self.rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, WHITE, self.rect, 2)
        txt = font_ui.render(self.text, True, WHITE)
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

btn_new = Button("새 게임", 400, 350, 200, 50)
btn_exit = Button("나가기", 400, 430, 200, 50)

prologue_lines = ["세상은 단 며칠 만에 무너졌다.", "이것은 당신이 어떻게 죽었는지에 대한 기록이다."]
pro_idx = 0

# --- 4. 메인 루프 전역 변수 초기화 ---
player = None
all_sprites = None
zombies = None
bullets = None
details = []

def init_game():
    global player, all_sprites, zombies, bullets, details
    player = Survivor()
    all_sprites = pygame.sprite.Group(player)
    zombies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    details = [] # 여기에 배경 파편 생성 로직 추가 가능

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)

# --- 5. 실행부 ---

while True:
    screen.fill(BLACK)
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if current_state == STATE_TITLE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_new.rect.collidepoint(event.pos):
                    current_state = STATE_PROLOGUE
                if btn_exit.rect.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
                    
        elif current_state == STATE_PROLOGUE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pro_idx += 1
                if pro_idx >= len(prologue_lines):
                    init_game() # 게임 데이터 생성
                    current_state = STATE_GAME
                    
        elif current_state == STATE_GAME:
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
                    for z in zombies:
                        if player.rect.inflate(40,40).colliderect(z.rect): z.kill()

    # --- 상태별 그리기 및 업데이트 ---
    if current_state == STATE_TITLE:
        title = font_title.render("PROJECT ZOMBOID CLONE", True, RED)
        screen.blit(title, (500 - title.get_width()//2, 200))
        btn_new.draw(screen)
        btn_exit.draw(screen)
        
    elif current_state == STATE_PROLOGUE:
        txt = font_ui.render(prologue_lines[pro_idx], True, WHITE)
        screen.blit(txt, (500 - txt.get_width()//2, 400))
        tip = font_ui.render("[ SPACE 키를 눌러 진행 ]", True, (100,100,100))
        screen.blit(tip, (500 - tip.get_width()//2, 700))
        
    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        if player.hp > 0:
            all_sprites.update()
            pygame.sprite.groupcollide(bullets, zombies, True, True)
            if pygame.sprite.spritecollide(player, zombies, False): player.hp -= 0.15
        
        all_sprites.draw(screen)
        ui_txt = font_ui.render(f"HP: {int(player.hp)} | AMMO: {player.ammo} | WEAPON: {player.weapon_mode}", True, WHITE)
        screen.blit(ui_txt, (20, 20))
        if player.hp <= 0:
            screen.blit(font_title.render("YOU DIED", True, RED), (400, 350))

    pygame.display.flip()
    clock.tick(FPS)