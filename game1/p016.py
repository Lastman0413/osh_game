import pygame
import sys
import math
import random

# --- 1. 초기화 및 설정 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Zomboid: Rebirth - The Honest Integration")
clock = pygame.time.Clock()

# 색상 및 상수
WHITE, BLACK, RED, GRAY, GREEN, BLUE, YELLOW = (255,255,255), (0,0,0), (220,20,20), (50,50,50), (40,180,40), (40,80,200), (255,255,100)
SKIN, ZOMBIE_SKIN = (235,195,165), (140,160,140)
BG_COLOR = (24, 26, 24)

# 폰트 로드
try:
    f_lg = pygame.font.SysFont("malgungothic", 55, bold=True)
    f_md = pygame.font.SysFont("malgungothic", 26, bold=True)
    f_sm = pygame.font.SysFont("malgungothic", 17, bold=True)
except:
    f_lg = pygame.font.SysFont("arial", 55, bold=True)
    f_md = pygame.font.SysFont("arial", 26, bold=True)
    f_sm = pygame.font.SysFont("arial", 17, bold=True)

# 게임 상태 및 데이터
STATE_MENU, STATE_SELECT, STATE_PROLOGUE, STATE_GAME, STATE_DEAD = "MENU", "SELECT", "PROLOGUE", "GAME", "DEAD"
curr_state = STATE_MENU
JOBS = {
    "Police": {"hp": 100, "glock": 100, "shotgun": 0, "speed": 2.4, "color": BLUE, "init_w": "GLOCK"},
    "Firefighter": {"hp": 220, "glock": 0, "shotgun": 0, "speed": 2.1, "color": RED, "init_w": "BAT"},
    "Survivalist": {"hp": 90, "glock": 20, "shotgun": 50, "speed": 3.0, "color": GREEN, "init_w": "SHOTGUN"}
}
PROLOGUE_LINES = ["세상은 단 며칠 만에 무너져 내렸다.", "이것은 당신이 어떻게 죽었는지에 대한 기록이다."]
prologue_idx = 0

# --- 2. 렌더링 엔진 (모든 시각 요소 통합) ---

def draw_entity(surf, x, y, color, move, walk_cnt, weapon="NONE", zombie=False):
    cx, cy = x, y
    skin = ZOMBIE_SKIN if zombie else SKIN
    swing = math.sin(walk_cnt * 0.22) * 12 if move else 0
    # 몸체 레이어
    pygame.draw.rect(surf, (30,30,30), (cx-10, cy+12+swing, 9, 16)) # 왼다리
    pygame.draw.rect(surf, (30,30,30), (cx+1, cy+12-swing, 9, 16)) # 오른다리
    pygame.draw.rect(surf, skin, (cx-19, cy-5-swing, 7, 18)) # 왼팔
    pygame.draw.rect(surf, color, (cx-13, cy-13, 26, 30)) # 몸통
    pygame.draw.rect(surf, skin, (cx-8, cy-25, 16, 12)) # 머리
    # 무기 레이어 (오른손 가시화)
    if not zombie:
        hx, hy = cx + 13, cy - 5 + swing
        if weapon == "BAT": pygame.draw.line(surf, (139,69,19), (hx, hy+5), (hx+20, hy-18), 7)
        elif weapon == "GLOCK": pygame.draw.rect(surf, (40,40,40), (hx+2, hy, 16, 8))
        elif weapon == "SHOTGUN": pygame.draw.rect(surf, (20,20,20), (hx+2, hy, 30, 10))
        pygame.draw.rect(surf, skin, (hx, hy, 9, 11)) # 오른손
    else:
        pygame.draw.rect(surf, skin, (cx+13, cy-15+swing, 7, 18)) # 좀비의 뻗은 팔

class Blood(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        s = random.randint(15, 30)
        self.image = pygame.Surface((s,s), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150,0,0,160), (s//2, s//2), s//2)
        self.rect = self.image.get_rect(center=(x,y))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target, spread=0):
        super().__init__()
        self.image = pygame.Surface((8,8), pygame.SRCALPHA); pygame.draw.circle(self.image, YELLOW, (4,4), 4)
        self.rect = self.image.get_rect(center=(x,y)); self.pos = pygame.Vector2(x,y)
        angle = math.degrees(math.atan2(target[1]-y, target[0]-x)) + spread
        self.vel = pygame.Vector2(22, 0).rotate(angle)
    def update(self):
        self.pos += self.vel; self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self, job):
        super().__init__()
        d = JOBS[job]
        self.job, self.hp, self.speed, self.color = job, d["hp"], d["speed"], d["color"]
        self.ammo_g, self.ammo_s = d["glock"], d["shotgun"]
        self.weapon, self.walk_cnt, self.moving, self.infected, self.last_shot = "BAT", 0, False, False, 0
        self.image = pygame.Surface((100,100), pygame.SRCALPHA); self.rect = self.image.get_rect(center=(500,400))
    def update(self):
        k = pygame.key.get_pressed(); move = pygame.Vector2(0,0); self.moving = False
        if k[pygame.K_w]: move.y -= 1
        if k[pygame.K_s]: move.y += 1
        if k[pygame.K_a]: move.x -= 1
        if k[pygame.K_d]: move.x += 1
        for i, w in enumerate(["BAT", "GLOCK", "SHOTGUN"]):
            if k[pygame.K_1 + i]: self.weapon = w
        if move.length() > 0:
            self.rect.center += move.normalize() * self.speed; self.walk_cnt += 1; self.moving = True
        if self.infected: self.hp -= 0.02
        self.image.fill((0,0,0,0)); draw_entity(self.image, 50, 50, self.color, self.moving, self.walk_cnt, self.weapon)

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target; self.image = pygame.Surface((100,100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(random.choice([-100, 1100]), random.randint(0, 800)))
        self.walk_cnt = random.random()*10
    def update(self):
        v = (pygame.Vector2(self.target.rect.center) - pygame.Vector2(self.rect.center))
        if v.length() > 0: self.rect.center += v.normalize() * 0.95
        self.walk_cnt += 1; self.image.fill((0,0,0,0)); draw_entity(self.image, 50, 50, (70,90,70), True, self.walk_cnt, zombie=True)

# --- 3. 게임 엔진 통합 ---

def draw_t(txt, f, c, x, y, center=True):
    s = f.render(txt, True, c)
    r = s.get_rect(center=(x,y)) if center else s.get_rect(topleft=(x,y))
    screen.blit(s, r)

def init_game(job):
    global p, all_s, zombies, bullets, bloods
    p = Survivor(job); all_s = pygame.sprite.Group(p)
    zombies, bullets, bloods = [pygame.sprite.Group() for _ in range(3)]

while True:
    screen.fill(BLACK); m_pos, m_down = pygame.mouse.get_pos(), False
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        if ev.type == pygame.MOUSEBUTTONDOWN: m_down = True
        if curr_state == STATE_PROLOGUE and ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            prologue_idx += 1
            if prologue_idx >= len(PROLOGUE_LINES): init_game(selected_job); curr_state = STATE_GAME

    if curr_state == STATE_MENU:
        draw_t("PROJECT ZOMBOID: REBIRTH", f_lg, RED, 500, 200)
        r = pygame.Rect(400, 450, 200, 55); pygame.draw.rect(screen, GRAY if r.collidepoint(m_pos) else (30,30,30), r)
        draw_t("NEW GAME", f_md, WHITE, 500, 477)
        if r.collidepoint(m_pos) and m_down: curr_state = STATE_SELECT

    elif curr_state == STATE_SELECT:
        draw_t("직업을 선택하십시오", f_md, WHITE, 500, 100)
        for i, (name, d) in enumerate(JOBS.items()):
            r = pygame.Rect(70+i*310, 200, 240, 500); hover = r.collidepoint(m_pos)
            pygame.draw.rect(screen, (20,20,20), r); pygame.draw.rect(screen, d["color"], r, 2 if hover else 1)
            draw_entity(screen, r.centerx, r.y+100, d["color"], True, pygame.time.get_ticks()*0.01, d["init_w"])
            draw_t(name, f_md, WHITE, r.centerx, r.y+220)
            if hover and m_down: selected_job = name; curr_state = STATE_PROLOGUE

    elif curr_state == STATE_PROLOGUE:
        draw_t(PROLOGUE_LINES[prologue_idx], f_md, WHITE, 500, 400); draw_t("[ SPACE TO CONTINUE ]", f_sm, GRAY, 500, 700)

    elif curr_state == STATE_GAME:
        screen.fill(BG_COLOR); bloods.draw(screen); now = pygame.time.get_ticks()
        if m_down and p.hp > 0:
            if p.weapon == "GLOCK" and p.ammo_g > 0 and now - p.last_shot > 300:
                bullets.add(Bullet(p.rect.centerx, p.rect.centery, m_pos)); p.ammo_g -= 1; p.last_shot = now
            elif p.weapon == "SHOTGUN" and p.ammo_s > 0 and now - p.last_shot > 850:
                for a in [-12, 0, 12]: bullets.add(Bullet(p.rect.centerx, p.rect.centery, m_pos, a))
                p.ammo_s -= 1; p.last_shot = now
            elif p.weapon == "BAT" and now - p.last_shot > 600:
                for z in zombies:
                    if pygame.Vector2(p.rect.center).distance_to(z.rect.center) < 60:
                        bloods.add(Blood(z.rect.centerx, z.rect.centery)); z.kill(); p.ammo_g += 5; p.last_shot = now
        
        if len(zombies) < 15 and random.random() < 0.035:
            z = Zombie(p); zombies.add(z); all_s.add(z)
        all_s.update(); bullets.update()
        for b in bullets:
            hits = pygame.sprite.groupcollide(bullets, zombies, True, True)
            for z_list in hits.values():
                for hz in z_list: bloods.add(Blood(hz.rect.centerx, hz.rect.centery))

        if pygame.sprite.spritecollide(p, zombies, False):
            p.hp -= 0.5
            if random.random() < 0.01: p.infected = True
        
        all_s.draw(screen); bullets.draw(screen)
        draw_t(f"HP: {int(p.hp)} | {p.weapon} | Ammo: {p.ammo_g if p.weapon=='GLOCK' else p.ammo_s}", f_sm, WHITE, 20, 20, False)
        if p.infected: draw_t("감염됨 (Infected)", f_sm, RED, 20, 50, False)
        if p.hp <= 0: curr_state = STATE_DEAD

    elif curr_state == STATE_DEAD:
        draw_t("THIS IS HOW YOU DIED", f_lg, RED, 500, 400); draw_t("Press R to Restart", f_md, WHITE, 500, 500)
        if pygame.key.get_pressed()[pygame.K_r]: curr_state = STATE_MENU; prologue_idx = 0

    pygame.display.flip(); clock.tick(60)