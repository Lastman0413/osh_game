

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
pygame.display.set_caption("Project Zomboid: Full Integration")
clock = pygame.time.Clock()

# 색상 및 폰트
WHITE, BLACK, RED, GRAY, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0), (40, 80, 200)
SKIN, ZOMBIE_SKIN = (235, 195, 165), (140, 160, 140)
BG_COLOR = (30, 35, 30)

try:
    font_main = pygame.font.SysFont("malgungothic", 35, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 18, bold=True)
    font_prologue = pygame.font.SysFont("malgungothic", 22, italic=True)
except:
    font_main = pygame.font.SysFont("arial", 35, bold=True)
    font_ui = pygame.font.SysFont("arial", 18, bold=True)
    font_prologue = pygame.font.SysFont("arial", 22, italic=True)

# 게임 상태 및 데이터
STATE_TITLE, STATE_SELECT, STATE_PROLOGUE, STATE_GAME = "TITLE", "SELECT", "PROLOGUE", "GAME"
current_state = STATE_TITLE
selected_job = None

JOBS = {
    "Police": {"hp": 100, "glock": 50, "shotgun": 0, "speed": 2.2, "color": BLUE, "desc": "권총 탄약 특화"},
    "Firefighter": {"hp": 160, "glock": 0, "shotgun": 0, "speed": 1.9, "color": (180, 40, 40), "desc": "높은 체력과 생존력"},
    "Survivalist": {"hp": 80, "glock": 10, "shotgun": 15, "speed": 2.6, "color": (60, 100, 60), "desc": "빠른 속도, 샷건 보유"}
}

PROLOGUE_LINES = [
    "세상은 단 며칠 만에 무너져 내렸다.",
    "이것은 당신이 어떻게 죽었는지에 대한 기록이다."
]
prologue_idx = 0

# --- 2. 통합 렌더링 함수 ---

def draw_animated_model(surface, x, y, color, is_moving, walk_cnt, weapon="NONE", is_zombie=False):
    cx, cy = x, y
    skin = ZOMBIE_SKIN if is_zombie else SKIN
    # 좀비는 더 느릿하게 흔들림
    swing = math.sin(walk_cnt * (0.15 if is_zombie else 0.22)) * 12 if is_moving else 0
    
    # 다리
    leg_c = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    pygame.draw.rect(surface, leg_c, (cx-9, cy+12 + swing, 7, 14))
    pygame.draw.rect(surface, leg_c, (cx+2, cy+12 - swing, 7, 14))
    
    # 왼팔
    pygame.draw.rect(surface, skin, (cx-18, cy-5 - swing, 6, 16))
    
    # 몸통
    pygame.draw.rect(surface, color, (cx-12, cy-12, 24, 26))
    
    # 머리
    pygame.draw.rect(surface, (70, 45, 35) if not is_zombie else (40, 50, 40), (cx-8, cy-26, 16, 15))
    pygame.draw.rect(surface, skin, (cx-7, cy-20, 14, 9))

    # 오른팔 및 무기 구현
    if not is_zombie:
        hand_x, hand_y = cx + 12, cy - 5 + swing
        if weapon == "BAT":
            pygame.draw.line(surface, (130, 90, 60), (hand_x + 2, hand_y + 5), (hand_x + 18, hand_y - 15), 6) # 방망이
        elif weapon == "GLOCK":
            pygame.draw.rect(surface, (40, 40, 40), (hand_x + 2, hand_y + 2, 12, 6)) # 권총
        elif weapon == "SHOTGUN":
            pygame.draw.rect(surface, (20, 20, 20), (hand_x + 2, hand_y + 2, 22, 8)) # 샷건
        pygame.draw.rect(surface, skin, (hand_x, hand_y, 8, 10)) # 오른손
    else:
        # 좀비 팔 (공격적인 포즈)
        pygame.draw.rect(surface, skin, (cx+12, cy-15 + swing, 6, 16))

# --- 3. 클래스 정의 ---

class Survivor(pygame.sprite.Sprite):
    def __init__(self, job):
        super().__init__()
        s = JOBS[job]
        self.job, self.hp, self.speed, self.color = job, s["hp"], s["speed"], s["color"]
        self.ammo_glock, self.ammo_shotgun = s["glock"], s["shotgun"]
        self.weapon_mode, self.walk_count, self.is_moving = "BAT", 0, False
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(500, 400))
        self.pos = pygame.Vector2(self.rect.center)

    def update(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        self.is_moving = False
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        if keys[pygame.K_1]: self.weapon_mode = "BAT"
        if keys[pygame.K_2]: self.weapon_mode = "GLOCK"
        if keys[pygame.K_3]: self.weapon_mode = "SHOTGUN"
        
        if move.length() > 0:
            self.pos += move.normalize() * self.speed
            self.walk_count += 1; self.is_moving = True
        
        self.rect.center = self.pos
        self.image.fill((0,0,0,0))
        draw_animated_model(self.image, 50, 50, self.color, self.is_moving, self.walk_count, self.weapon_mode)

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.color = random.choice([BLUE, RED, GREEN])
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(random.choice([-50, 1050]), random.randint(0, 800)))
        self.pos = pygame.Vector2(self.rect.center)
        self.walk_count = random.random() * 10
    def update(self):
        dir_v = (self.target.pos - self.pos)
        if dir_v.length() > 0: self.pos += dir_v.normalize() * 0.8
        self.walk_count += 1
        self.rect.center = self.pos
        self.image.fill((0,0,0,0))
        draw_animated_model(self.image, 50, 50, self.color, True, self.walk_count, is_zombie=True)

# --- 4. 메인 루프 ---

def init_game(job):
    global player, all_sprites, zombies
    player = Survivor(job)
    all_sprites, zombies = pygame.sprite.Group(player), pygame.sprite.Group()

while True:
    screen.fill(BLACK)
    m_p = pygame.mouse.get_pos()
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if current_state == STATE_TITLE and e.type == pygame.MOUSEBUTTONDOWN: current_state = STATE_SELECT
        elif current_state == STATE_SELECT and e.type == pygame.MOUSEBUTTONDOWN:
            for i, name in enumerate(JOBS.keys()):
                r = pygame.Rect(100+i*300, 300, 200, 350)
                if r.collidepoint(m_p): selected_job = name; current_state = STATE_PROLOGUE
        elif current_state == STATE_PROLOGUE and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                prologue_idx += 1
                if prologue_idx >= len(PROLOGUE_LINES): init_game(selected_job); current_state = STATE_GAME

    if current_state == STATE_SELECT:
        screen.blit(font_main.render("직업을 선택하십시오", True, WHITE), (330, 150))
        for i, (name, data) in enumerate(JOBS.items()):
            r = pygame.Rect(100+i*300, 300, 200, 350)
            pygame.draw.rect(screen, (30,30,30), r)
            pygame.draw.rect(screen, data["color"], r, 2)
            draw_animated_model(screen, r.centerx, r.y+100, data["color"], True, pygame.time.get_ticks()*0.01)
            n_t = font_ui.render(name, True, WHITE)
            screen.blit(n_t, (r.centerx - n_t.get_width()//2, r.y + 180))

    elif current_state == STATE_PROLOGUE:
        p_t = font_prologue.render(PROLOGUE_LINES[prologue_idx], True, WHITE)
        screen.blit(p_t, (SCREEN_WIDTH//2 - p_t.get_width()//2, 380))
        screen.blit(font_ui.render("[ SPACE ]", True, GRAY), (470, 700))

    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        if len(zombies) < 10: 
            z = Zombie(player); zombies.add(z); all_sprites.add(z)
        all_sprites.update()
        all_sprites.draw(screen)
        # 무기 정보 HUD
        weapon_map = {"BAT":"방망이", "GLOCK":"권총", "SHOTGUN":"샷건"}
        screen.blit(font_ui.render(f"HP: {int(player.hp)} | 무기: {weapon_map[player.weapon_mode]}", True, WHITE), (20, 20))

    pygame.display.flip()
    clock.tick(FPS)