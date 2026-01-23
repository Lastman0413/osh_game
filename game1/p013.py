
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
pygame.display.set_caption("Project Zomboid: Rebirth")
clock = pygame.time.Clock()

# 색상 및 폰트 설정
WHITE, BLACK, RED, GRAY, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (200, 0, 0), (50, 50, 50), (0, 200, 0), (40, 80, 200)
SKIN, ZOMBIE_SKIN = (235, 195, 165), (140, 160, 140)
BG_COLOR = (30, 35, 30)

# 폰트 최적화 (사이즈 조정으로 가독성 확보)
try:
    font_main = pygame.font.SysFont("malgungothic", 35, bold=True)
    font_ui = pygame.font.SysFont("malgungothic", 17, bold=True)
    font_prologue = pygame.font.SysFont("malgungothic", 22, italic=True)
except:
    font_main = pygame.font.SysFont("arial", 35, bold=True)
    font_ui = pygame.font.SysFont("arial", 17, bold=True)
    font_prologue = pygame.font.SysFont("arial", 22, italic=True)

# 게임 상태 및 데이터
STATE_TITLE, STATE_SELECT, STATE_PROLOGUE, STATE_GAME = "TITLE", "SELECT", "PROLOGUE", "GAME"
current_state = STATE_TITLE
selected_job = None

JOBS = {
    "Police": {"hp": 100, "glock": 40, "shotgun": 0, "speed": 2.2, "color": BLUE, "desc": "권총 탄약 특화"},
    "Firefighter": {"hp": 160, "glock": 0, "shotgun": 0, "speed": 1.9, "color": (180, 40, 40), "desc": "높은 체력과 생존력"},
    "Survivalist": {"hp": 80, "glock": 5, "shotgun": 12, "speed": 2.6, "color": (60, 100, 60), "desc": "빠른 속도, 샷건 보유"}
}

PROLOGUE_LINES = [
    "세상은 단 며칠 만에 무너져 내렸다.",
    "정부는 침묵했고, 거리는 굶주린 자들로 가득 찼다.",
    "이것은 당신이 어떻게 생존했느냐에 대한 이야기가 아니다.",
    "이것은 당신이 어떻게 죽었는지에 대한 기록이다."
]
prologue_idx = 0

# --- 2. 핵심 드로잉 함수 ---

def draw_entity_model(surface, x, y, color, is_moving, walk_cnt, is_zombie=False):
    """캐릭터와 좀비의 팔다리 애니메이션 모델링"""
    cx, cy = x, y
    skin = ZOMBIE_SKIN if is_zombie else SKIN
    speed_factor = 0.15 if is_zombie else 0.22
    swing = math.sin(walk_cnt * speed_factor) * 12 if is_moving else 0
    
    # 다리 (하의)
    leg_c = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    pygame.draw.rect(surface, leg_c, (cx-9, cy+12 + swing, 7, 14))
    pygame.draw.rect(surface, leg_c, (cx+2, cy+12 - swing, 7, 14))
    # 팔
    pygame.draw.rect(surface, skin, (cx-18, cy-5 - swing, 6, 16))
    pygame.draw.rect(surface, skin, (cx+12, cy-5 + swing, 6, 16))
    # 몸통
    pygame.draw.rect(surface, color, (cx-12, cy-12, 24, 26))
    # 머리
    pygame.draw.rect(surface, (70, 45, 35) if not is_zombie else (40, 50, 40), (cx-8, cy-26, 16, 15))
    pygame.draw.rect(surface, skin, (cx-7, cy-20, 14, 9))

# --- 3. 클래스 정의 ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, spread=0):
        super().__init__()
        self.image = pygame.Surface((6, 6)); self.image.fill((255, 255, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        dir_vec = pygame.Vector2(target_pos) - self.pos
        angle = math.degrees(math.atan2(dir_vec.y, dir_vec.x)) + spread if dir_vec.length() > 0 else spread
        self.velocity = pygame.Vector2(16, 0).rotate(angle)
    def update(self):
        self.pos += self.velocity; self.rect.center = self.pos
        if not screen.get_rect().contains(self.rect): self.kill()

class Survivor(pygame.sprite.Sprite):
    def __init__(self, job):
        super().__init__()
        s = JOBS[job]
        self.job, self.hp, self.speed, self.color = job, s["hp"], s["speed"], s["color"]
        self.ammo_glock, self.ammo_shotgun = s["glock"], s["shotgun"]
        self.weapon_mode, self.walk_count, self.is_moving = "BAT", 0, False
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
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
        if move.length() > 0:
            self.pos += move.normalize() * self.speed
            self.walk_count += 1; self.is_moving = True
        self.rect.center = self.pos
        self.image.fill((0,0,0,0))
        draw_entity_model(self.image, 40, 40, self.color, self.is_moving, self.walk_count)

class Zombie(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        job_key = random.choice(list(JOBS.keys()))
        self.target, self.color = target, JOBS[job_key]["color"]
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(random.choice([-50, 1050]), random.randint(0, 800)))
        self.pos = pygame.Vector2(self.rect.center)
        self.walk_count = random.random() * 10
    def update(self):
        if self.target.hp > 0:
            dir_v = (self.target.pos - self.pos)
            if dir_v.length() > 0: self.pos += dir_v.normalize() * 0.85
            self.walk_count += 1
        self.rect.center = self.pos
        self.image.fill((0,0,0,0))
        draw_entity_model(self.image, 40, 40, self.color, True, self.walk_count, is_zombie=True)

# --- 4. 메인 루프 ---

def init_game(job):
    global player, all_sprites, zombies, bullets
    player = Survivor(job)
    all_sprites = pygame.sprite.Group(player)
    zombies, bullets = pygame.sprite.Group(), pygame.sprite.Group()

SPAWN_Z = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_Z, 2500)

while True:
    screen.fill(BLACK)
    m_p = pygame.mouse.get_pos()
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if current_state == STATE_TITLE and e.type == pygame.MOUSEBUTTONDOWN:
            current_state = STATE_SELECT
            
        elif current_state == STATE_SELECT and e.type == pygame.MOUSEBUTTONDOWN:
            for i, name in enumerate(JOBS.keys()):
                r = pygame.Rect(100 + i*300, 300, 200, 350)
                if r.collidepoint(m_p):
                    selected_job = name
                    current_state = STATE_PROLOGUE
                    
        elif current_state == STATE_PROLOGUE and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                prologue_idx += 1
                if prologue_idx >= len(PROLOGUE_LINES):
                    init_game(selected_job); current_state = STATE_GAME
        
        elif current_state == STATE_GAME:
            if e.type == SPAWN_Z and len(zombies) < 15:
                z = Zombie(player); zombies.add(z); all_sprites.add(z)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                bullets.add(Bullet(player.rect.centerx, player.rect.centery, m_p))

    # --- 렌더링 영역 ---
    if current_state == STATE_TITLE:
        t = font_main.render("PROJECT ZOMBOID: REBIRTH", True, RED)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 300))
        screen.blit(font_ui.render("클릭하여 시작", True, WHITE), (440, 550))

    elif current_state == STATE_SELECT:
        screen.blit(font_main.render("직업을 선택하십시오", True, WHITE), (330, 150))
        for i, (name, data) in enumerate(JOBS.items()):
            r = pygame.Rect(100 + i*300, 300, 200, 350)
            is_hover = r.collidepoint(m_p)
            pygame.draw.rect(screen, (40,40,40) if is_hover else (20,20,20), r)
            pygame.draw.rect(screen, data["color"], r, 3)
            
            # 캐릭터 미리보기 (박스 중앙 상단 배치)
            draw_entity_model(screen, r.centerx, r.y + 100, data["color"], True, pygame.time.get_ticks()*0.01)
            
            # 텍스트 중앙 정렬 (박스 안으로 제한)
            name_t = font_ui.render(name, True, WHITE)
            desc_t = font_ui.render(data["desc"], True, GRAY)
            screen.blit(name_t, (r.centerx - name_t.get_width()//2, r.y + 180))
            screen.blit(desc_t, (r.centerx - desc_t.get_width()//2, r.y + 230))

    elif current_state == STATE_PROLOGUE:
        p_surf = font_prologue.render(PROLOGUE_LINES[prologue_idx], True, WHITE)
        screen.blit(p_surf, (SCREEN_WIDTH//2 - p_surf.get_width()//2, 380))
        screen.blit(font_ui.render("[ SPACE ] 키를 눌러 진행", True, GRAY), (410, 700))

    elif current_state == STATE_GAME:
        screen.fill(BG_COLOR)
        all_sprites.update(); bullets.update()
        pygame.sprite.groupcollide(bullets, zombies, True, True)
        all_sprites.draw(screen); bullets.draw(screen)
        screen.blit(font_ui.render(f"HP: {int(player.hp)} | JOB: {player.job}", True, WHITE), (20, 20))

    pygame.display.flip()
    clock.tick(FPS)