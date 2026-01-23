import pygame
import sys
import math
import random
import time

# --- 1. 엔진 및 환경 설정 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Zomboid: Rebirth - Ultimate Integration")
clock = pygame.time.Clock()

# 색상 및 상수
WHITE, BLACK, RED, GRAY, GREEN, BLUE, YELLOW = (255,255,255), (0,0,0), (200,20,20), (50,50,50), (40,180,40), (40,80,200), (255,255,100)
SKIN, ZOMBIE_SKIN = (235,195,165), (140,160,140)
BG_COLOR = (28, 30, 28)

# 폰트 로드 (크기별 최적화)
try:
    font_lg = pygame.font.SysFont("malgungothic", 55, bold=True)
    font_md = pygame.font.SysFont("malgungothic", 28, bold=True)
    font_sm = pygame.font.SysFont("malgungothic", 18, bold=True)
    font_prologue = pygame.font.SysFont("malgungothic", 24, italic=True)
except:
    font_lg = pygame.font.SysFont("arial", 55, bold=True)
    font_md = pygame.font.SysFont("arial", 28, bold=True)
    font_sm = pygame.font.SysFont("arial", 18, bold=True)
    font_prologue = pygame.font.SysFont("arial", 24, italic=True)

# 게임 상태 관리
STATE_MENU, STATE_SELECT, STATE_PROLOGUE, STATE_GAME, STATE_DEAD = "MENU", "SELECT", "PROLOGUE", "GAME", "DEAD"
current_state = STATE_MENU

JOBS = {
    "Police": {"hp": 100, "glock": 60, "shotgun": 0, "speed": 2.3, "color": BLUE, "desc": "권총 특화, 명중률 높음"},
    "Firefighter": {"hp": 180, "glock": 0, "shotgun": 0, "speed": 2.0, "color": RED, "desc": "강인한 맷집, 감염 저항"},
    "Survivalist": {"hp": 85, "glock": 15, "shotgun": 20, "speed": 2.7, "color": GREEN, "desc": "샷건 보유, 빠른 기동성"}
}

PROLOGUE_TEXT = [
    "세상은 단 며칠 만에 무너져 내렸다.",
    "정부는 침묵했고, 거리는 굶주린 자들로 가득 찼다.",
    "이것은 당신이 어떻게 생존했느냐에 대한 이야기가 아니다.",
    "이것은 당신이 어떻게 죽었는지에 대한 기록이다."
]
prologue_idx = 0

# --- 2. 핵심 클래스 ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, spread=0):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        dir_vec = pygame.Vector2(target_pos) - self.pos
        angle = math.degrees(math.atan2(dir_vec.y, dir_vec.x)) + spread
        self.velocity = pygame.Vector2(20, 0).rotate(angle)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

def draw_entity_model(surface, x, y, color, is_moving, walk_cnt, weapon="NONE", is_zombie=False):
    """모든 캐릭터 렌더링 통합 (팔다리 애니메이션 + 무기 가시화)"""
    cx, cy = x, y
    skin_c = ZOMBIE_SKIN if is_zombie else SKIN
    swing = math.sin(walk_cnt * 0.22) * 12 if is_moving else 0
    
    # 다리
    leg_c = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    pygame.draw.rect(surface, leg_c, (cx-9, cy+12 + swing, 8, 15))
    pygame.draw.rect(surface, leg_c, (cx+1, cy+12 - swing, 8, 15))
    # 왼팔
    pygame.draw.rect(surface, skin_c, (cx-18, cy-5 - swing, 6, 16))
    # 몸통
    pygame.draw.rect(surface, color, (cx-12, cy-12, 24, 28))
    # 머리
    pygame.draw.rect(surface, (70, 45, 35) if not is_zombie else (40, 50, 40), (cx-8, cy-25, 16, 14))
    pygame.draw.rect(surface, skin_c, (cx-7, cy-18, 14, 8))

    # 무기 가시화 (오른손)
    if not is_zombie:
        hand_x, hand_y = cx + 12, cy - 5 + swing
        if weapon == "BAT":
            pygame.draw.line(surface, (130, 90, 60), (hand_x, hand_y+5), (hand_x+18, hand_y-18), 6)
        elif weapon == "GLOCK":
            pygame.draw.rect(surface, (40, 40, 40), (hand_x+2, hand_y, 14, 7))
        elif weapon == "SHOTGUN":
            pygame.draw.rect(surface, (20, 20, 20), (hand_x+2, hand_y, 26, 9))
        pygame.draw.rect(surface, skin_c, (hand_x, hand_y, 8, 10)) # 오른손
    else:
        # 좀비 팔 (앞으로 나란히)
        pygame.draw.rect(surface, skin_c, (cx+12, cy-15 + swing, 6, 16))

class Survivor(pygame.sprite.Sprite):
    def __init__(self, job_name):
        super().__init__()
        s = JOBS[job_name]
        self.job, self.hp, self.max_hp, self.speed, self.color = job_name, s["hp"], s["hp"], s["speed"], s["color"]
        self.ammo_glock, self.ammo_shotgun = s["glock"], s["shotgun"]
        self.weapon_mode, self.walk_count, self.is_moving = "BAT", 0, False
        self.is_infected = False
        self.last_shot = 0
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
        if self.is_infected: self.hp -= 0.015
        self.image.fill((0,0,0,0))
        draw_entity_model(self.image, 50, 50, self.color, self.is_moving, self.walk_count, self.weapon_mode)

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(random.choice([-100, 1100]), random.randint(0, 800)))
        self.pos = pygame.Vector2(self.rect.center)
        self.walk_count = random.random() * 10
        self.color = random.choice([BLUE, RED, GREEN])
    def update(self):
        dir_v = (self.target.pos - self.pos)
        if dir_v.length() > 0: self.pos += dir_v.normalize() * 0.95
        self.walk_count += 1
        self.rect.center = self.pos
        self.image.fill((0,0,0,0))
        draw_entity_model(self.image, 50, 50, self.color, True, self.walk_count, is_zombie=True)

# --- 3. 통합 시스템 엔진 ---

def draw_text(text, font, color, x, y, align="center"):
    surf = font.render(text, True, color)
    if align == "center": rect = surf.get_rect(center=(x, y))
    else: rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)

def init_game(job):
    global player, all_sprites, zombies, bullets, start_time
    player = Survivor(job)
    all_sprites = pygame.sprite.Group(player)
    zombies, bullets = pygame.sprite.Group(), pygame.sprite.Group()
    start_time = time.time()

# 메인 루프
while True:
    screen.fill(BLACK)
    m_p = pygame.mouse.get_pos()
    m_clicked = False
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN: m_clicked = True

    if current_state == STATE_MENU:
        draw_text("PROJECT ZOMBOID: REBIRTH", font_lg, RED, SCREEN_WIDTH//2, 200)
        btns = [("NEW GAME", 400), ("LOAD GAME", 480), ("QUIT", 560)]
        for text, y in btns:
            r = pygame.Rect(SCREEN_WIDTH//2-120, y-25, 240, 50)
            is_hover = r.collidepoint(m_p)
            pygame.draw.rect(screen, GRAY if is_hover else (30,30,30), r)
            draw_text(text, font_md, WHITE, SCREEN_WIDTH//2, y)
            if is_hover and m_clicked:
                if text == "NEW GAME": current_state = STATE_SELECT
                if text == "QUIT": pygame.quit(); sys.exit()

    elif current_state == STATE_SELECT:
        draw_text("CHOOSE YOUR CHARACTER", font_md, WHITE, SCREEN_WIDTH//2, 120)
        for i, (name, data) in enumerate(JOBS.items()):
            r = pygame.Rect(80 + i*310, 250, 220, 450)
            is_hover = r.collidepoint(m_p)
            pygame.draw.rect(screen, (20,20,20), r); pygame.draw.rect(screen, data["color"], r, 3 if is_hover else 1)
            # 미리보기 모델 (팔다리 애니메이션 포함)
            draw_entity_model(screen, r.centerx, r.y+100, data["color"], True, pygame.time.get_ticks()*0.01, "GLOCK" if i==0 else "BAT")
            draw_text(name, font_md, WHITE, r.centerx, r.y+200)
            draw_text(data["desc"], font_sm, GRAY, r.centerx, r.y+250)
            if is_hover and m_clicked:
                selected_job = name; current_state = STATE_PROLOGUE

    elif current_state == STATE_PROLOGUE:
        draw_text(PROLOGUE_TEXT[prologue_idx], font_prologue, WHITE, SCREEN_WIDTH//2, 400)
        draw_text("[ SPACE TO CONTINUE ]", font_sm, GRAY, SCREEN_WIDTH//2, 700)
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            time.sleep(0.2)
            prologue_idx += 1
            if prologue_idx >= len(PROLOGUE_TEXT): init_game(selected_job); current_state = STATE_GAME

    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        now = pygame.time.get_ticks()
        # 전투 발사 로직 (복구)
        if m_clicked and player.hp > 0:
            if player.weapon_mode == "GLOCK" and player.ammo_glock > 0 and now - player.last_shot > 300:
                bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p))
                player.ammo_glock -= 1; player.last_shot = now
            elif player.weapon_mode == "SHOTGUN" and player.ammo_shotgun > 0 and now - player.last_shot > 800:
                for a in [-12, 0, 12]: bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p, a))
                player.ammo_shotgun -= 1; player.last_shot = now
            elif player.weapon_mode == "BAT" and now - player.last_shot > 600:
                hits = pygame.sprite.spritecollide(player, zombies, True)
                if hits and random.random() < 0.4: player.ammo_glock += 5 # 루팅 복구
                player.last_shot = now

        if len(zombies) < 15 and random.random() < 0.03:
            z = Zombie(player); zombies.add(z); all_sprites.add(z)

        all_sprites.update(); bullets.update()
        pygame.sprite.groupcollide(bullets, zombies, True, True)
        if pygame.sprite.spritecollide(player, zombies, False):
            player.hp -= 0.4
            if random.random() < 0.008: player.is_infected = True # 감염 복구
        
        all_sprites.draw(screen); bullets.draw(screen)
        # HUD 복구
        draw_text(f"HP: {int(player.hp)} | WEAPON: {player.weapon_mode} | AMMO: {player.ammo_glock if player.weapon_mode=='GLOCK' else player.ammo_shotgun}", font_sm, WHITE, 20, 20, "left")
        if player.is_infected: draw_text("INFECTED", font_sm, RED, 20, 50, "left")
        if player.hp <= 0: current_state = STATE_DEAD

    elif current_state == STATE_DEAD:
        draw_text("THIS IS HOW YOU DIED", font_lg, RED, SCREEN_WIDTH//2, 350)
        draw_text("PRESS R TO RESTART", font_md, WHITE, SCREEN_WIDTH//2, 450)
        if pygame.key.get_pressed()[pygame.K_r]:
            prologue_idx = 0; current_state = STATE_MENU

    pygame.display.flip()
    clock.tick(FPS)