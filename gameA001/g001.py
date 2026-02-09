import pygame
import math
import random

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
FPS = 60
TILE_SIZE = 40

# 색상
COLOR_BG = (30, 30, 35)
COLOR_WALL = (100, 90, 80)
COLOR_WALL_TOP = (120, 110, 100)
COLOR_FLOOR = (180, 170, 150)
COLOR_GRID = (160, 150, 130)
COLOR_DOOR = (139, 90, 60)
COLOR_ZOMBIE_BODY = (80, 120, 80)
COLOR_ZOMBIE_HEAD = (100, 140, 100)
COLOR_ITEM = (255, 215, 0)
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 203, 164)

def to_iso(x, y):
    return (x - y), (x + y) / 2

# --- 집 맵 ---
class House:
    def __init__(self):
        self.origin_x = 3
        self.origin_y = 3
        self.tw = 15
        self.th = 12
        self.wall_h = 90
        self.wall_d = 15
        
    def get_floor_rect(self):
        return pygame.Rect(
            (self.origin_x + 0.5) * TILE_SIZE,
            (self.origin_y + 0.5) * TILE_SIZE,
            (self.tw - 1) * TILE_SIZE,
            (self.th - 1) * TILE_SIZE
        )

# --- 아빠 캐릭터 (생존자) ---
class Survivor:
    def __init__(self, x, y):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        
        # 외형
        self.limb_len = 20
        self.body_h = 30
        self.body_w = 22
        self.head_r = 14
        self.head_color = (255, 203, 164)
        self.body_color = (70, 130, 180)
        self.pants_color = (40, 60, 80)
        self.hair_color = (50, 40, 30)
        self.speed = 5
        
        # 생존 스탯
        self.health = 100
        self.hunger = 100
        self.stamina = 100
        self.alive = True
        
        # 인벤토리
        self.inventory = []
        
    def update(self, house, zombies):
        if not self.alive:
            return
            
        # 이동
        move_vec = pygame.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        sm = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w]: sm.y -= 1
        if keys[pygame.K_s]: sm.y += 1
        if keys[pygame.K_a]: sm.x -= 1
        if keys[pygame.K_d]: sm.x += 1
        
        if sm.length() > 0:
            sm = sm.normalize()
            move_vec = pygame.Vector2(sm.x + sm.y, -sm.x + sm.y).normalize() * self.speed
            self.look_dir = sm
            self.walk_count += 0.2
            self.stamina = max(0, self.stamina - 0.05)
        else:
            self.walk_count = 0
            self.stamina = min(100, self.stamina + 0.1)
        
        # 충돌 체크
        if move_vec.length() > 0:
            walkable = house.get_floor_rect()
            
            self.world_pos.x += move_vec.x
            if not walkable.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.x -= move_vec.x
            
            self.world_pos.y += move_vec.y
            if not walkable.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.y -= move_vec.y
        
        # 배고픔 감소
        self.hunger = max(0, self.hunger - 0.01)
        
        # 배고프면 체력 감소
        if self.hunger < 20:
            self.health = max(0, self.health - 0.02)
        
        # 좀비 충돌
        for zombie in zombies:
            if zombie.alive and self.world_pos.distance_to(zombie.world_pos) < 30:
                self.health -= 0.5
        
        # 사망 체크
        if self.health <= 0:
            self.alive = False
    
    def pickup_item(self, item):
        self.inventory.append(item)
        if item["type"] == "food":
            self.hunger = min(100, self.hunger + 30)
        elif item["type"] == "medkit":
            self.health = min(100, self.health + 50)
    
    def draw(self, surface, cam_off):
        if not self.alive:
            # 사망 시 누워있는 모습
            iso_p = to_iso(self.world_pos.x, self.world_pos.y)
            cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
            pygame.draw.ellipse(surface, (100, 100, 100), (cx - 30, cy - 10, 60, 20))
            return
        
        iso_p = to_iso(self.world_pos.x, self.world_pos.y)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
        
        swing = math.sin(self.walk_count) * (self.limb_len / 2.5)
        bobbing = abs(math.sin(self.walk_count)) * 2.5
        pelvis_y = cy - self.limb_len
        is_back = self.look_dir.y < -0.1
        draw_w = self.body_w - 4 if abs(self.look_dir.x) > 0.5 else self.body_w
        
        # 배낭
        bag_w, bag_h = draw_w + 2, max(8, self.body_h - 12)
        bag_rect = (cx - bag_w//2, pelvis_y - self.body_h + 8 + bobbing, bag_w, bag_h)
        if not is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        # 바지
        pants_h = self.body_h // 2
        pygame.draw.rect(surface, self.pants_color, (cx - draw_w//2, pelvis_y - pants_h, draw_w, pants_h))
        
        # 다리
        pygame.draw.line(surface, COLOR_LIMB, (cx - 4, pelvis_y), (cx - 4 - swing/2, cy + swing/2), 2)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 4, pelvis_y), (cx + 4 + swing/2, cy - swing/2), 2)
        
        # 상의
        body_top = pelvis_y - pants_h
        body_rect = (cx - draw_w//2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h)
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (200, 200, 200), body_rect, 1)
        
        if is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        # 팔
        shoulder_y = body_top - (self.body_h - pants_h) + 3
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y), 
                        (cx - draw_w//2 - 8, shoulder_y + 18 - swing), 2)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y), 
                        (cx + draw_w//2 + 8, shoulder_y + 18 + swing), 2)
        
        # 머리
        head_y = shoulder_y - 8
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)
        
        # 머리카락
        if not is_back:
            pygame.draw.ellipse(surface, self.hair_color, 
                               (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r))
        else:
            pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
        
        pygame.draw.circle(surface, (220, 220, 220), (int(cx), int(head_y)), self.head_r, 1)
        
        # 눈
        if not is_back:
            eye_x, eye_y = cx + self.look_dir.x * 3, head_y + self.look_dir.y * 1.5
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x - 4), int(eye_y)), 3)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x + 4), int(eye_y)), 3)
            pygame.draw.circle(surface, (50, 50, 50), (int(eye_x - 4), int(eye_y)), 2)
            pygame.draw.circle(surface, (50, 50, 50), (int(eye_x + 4), int(eye_y)), 2)

# --- 좀비 ---
class Zombie:
    def __init__(self, x, y):
        self.world_pos = pygame.Vector2(x, y)
        self.walk_count = 0
        self.speed = 2
        self.alive = True
        self.health = 50
        
    def update(self, target_pos, house):
        if not self.alive:
            return
        
        # 생존자 추적
        diff = target_pos - self.world_pos
        if diff.length() > 10:
            move_vec = diff.normalize() * self.speed
            self.walk_count += 0.15
        else:
            move_vec = pygame.Vector2(0, 0)
            self.walk_count = 0
        
        # 이동
        if move_vec.length() > 0:
            walkable = house.get_floor_rect()
            
            self.world_pos.x += move_vec.x
            if not walkable.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.x -= move_vec.x
            
            self.world_pos.y += move_vec.y
            if not walkable.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.y -= move_vec.y
    
    def draw(self, surface, cam_off):
        if not self.alive:
            return
        
        iso_p = to_iso(self.world_pos.x, self.world_pos.y)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
        
        wobble = math.sin(self.walk_count * 2) * 3
        
        # 다리 (비틀거림)
        pygame.draw.line(surface, (100, 120, 100), (cx - 5, cy), (cx - 5 + wobble, cy + 15), 3)
        pygame.draw.line(surface, (100, 120, 100), (cx + 5, cy), (cx + 5 - wobble, cy + 15), 3)
        
        # 몸통
        pygame.draw.rect(surface, COLOR_ZOMBIE_BODY, (cx - 10, cy - 35, 20, 25))
        
        # 팔 (늘어진)
        pygame.draw.line(surface, (100, 120, 100), (cx - 10, cy - 30), (cx - 15, cy - 15), 3)
        pygame.draw.line(surface, (100, 120, 100), (cx + 10, cy - 30), (cx + 15, cy - 15), 3)
        
        # 머리
        pygame.draw.circle(surface, COLOR_ZOMBIE_HEAD, (int(cx), int(cy - 45)), 10)
        
        # 눈 (빨강)
        pygame.draw.circle(surface, (200, 0, 0), (int(cx - 3), int(cy - 45)), 2)
        pygame.draw.circle(surface, (200, 0, 0), (int(cx + 3), int(cy - 45)), 2)

# --- 아이템 ---
class Item:
    def __init__(self, x, y, item_type):
        self.world_pos = pygame.Vector2(x, y)
        self.type = item_type  # "food", "medkit"
        self.picked = False
        
    def draw(self, surface, cam_off):
        if self.picked:
            return
        
        iso_p = to_iso(self.world_pos.x, self.world_pos.y)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
        
        # 빛나는 효과
        pygame.draw.circle(surface, (255, 255, 200), (int(cx), int(cy)), 15, 2)
        
        if self.type == "food":
            # 음식 (빵)
            pygame.draw.rect(surface, (200, 150, 100), (cx - 8, cy - 5, 16, 10), border_radius=3)
        elif self.type == "medkit":
            # 의료 키트 (십자가)
            pygame.draw.rect(surface, (255, 255, 255), (cx - 8, cy - 8, 16, 16))
            pygame.draw.line(surface, (255, 0, 0), (cx, cy - 6), (cx, cy + 6), 3)
            pygame.draw.line(surface, (255, 0, 0), (cx - 6, cy), (cx + 6, cy), 3)

# --- UI 그리기 ---
def draw_ui(screen, survivor):
    font = pygame.font.SysFont('malgungothic', 24)
    
    # 체력 바
    bar_x, bar_y = 20, 20
    bar_w, bar_h = 200, 25
    
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
    health_w = int((survivor.health / 100) * bar_w)
    pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, health_w, bar_h))
    text = font.render(f"체력: {int(survivor.health)}", True, (255, 255, 255))
    screen.blit(text, (bar_x + 5, bar_y + 3))
    
    # 배고픔 바
    bar_y += 35
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
    hunger_w = int((survivor.hunger / 100) * bar_w)
    pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, hunger_w, bar_h))
    text = font.render(f"배고픔: {int(survivor.hunger)}", True, (255, 255, 255))
    screen.blit(text, (bar_x + 5, bar_y + 3))
    
    # 스태미나 바
    bar_y += 35
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
    stamina_w = int((survivor.stamina / 100) * bar_w)
    pygame.draw.rect(screen, (100, 150, 255), (bar_x, bar_y, stamina_w, bar_h))
    text = font.render(f"체력: {int(survivor.stamina)}", True, (255, 255, 255))
    screen.blit(text, (bar_x + 5, bar_y + 3))
    
    # 인벤토리
    inv_text = font.render(f"인벤토리: {len(survivor.inventory)}개", True, (255, 255, 255))
    screen.blit(inv_text, (bar_x, bar_y + 40))
    
    # 사망 메시지
    if not survivor.alive:
        big_font = pygame.font.SysFont('malgungothic', 72)
        death_text = big_font.render("사망", True, (255, 0, 0))
        text_rect = death_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(death_text, text_rect)

# --- 맵 렌더링 ---
def render_house(screen, house, cam_off):
    # 바닥
    for tx in range(house.tw):
        for ty in range(house.th):
            wx = (house.origin_x + tx) * TILE_SIZE
            wy = (house.origin_y + ty) * TILE_SIZE
            ix, iy = to_iso(wx, wy)
            
            pts = [
                (ix + cam_off[0], iy + cam_off[1]),
                (ix + TILE_SIZE + cam_off[0], iy + TILE_SIZE/2 + cam_off[1]),
                (ix + cam_off[0], iy + TILE_SIZE + cam_off[1]),
                (ix - TILE_SIZE + cam_off[0], iy + TILE_SIZE/2 + cam_off[1])
            ]
            pygame.draw.polygon(screen, COLOR_FLOOR, pts)
            pygame.draw.polygon(screen, COLOR_GRID, pts, 1)
    
    # 벽 (북쪽, 서쪽)
    # 북쪽
    bx, by = house.origin_x * TILE_SIZE, house.origin_y * TILE_SIZE
    ex, ey = (house.origin_x + house.tw) * TILE_SIZE, house.origin_y * TILE_SIZE
    b_iso, e_iso = to_iso(bx, by), to_iso(ex, ey)
    
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - house.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - house.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)
    
    # 서쪽
    bx, by = house.origin_x * TILE_SIZE, house.origin_y * TILE_SIZE
    ex, ey = house.origin_x * TILE_SIZE, (house.origin_y + house.th) * TILE_SIZE
    b_iso, e_iso = to_iso(bx, by), to_iso(ex, ey)
    
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - house.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - house.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)

# --- 메인 ---
def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("좀보이드 스타일 - 생존 게임")
    clock = pygame.time.Clock()
    
    house = House()
    survivor = Survivor(300, 300)
    
    # 좀비 생성 (3마리)
    zombies = [
        Zombie(400, 200),
        Zombie(500, 400),
        Zombie(200, 450)
    ]
    
    # 아이템 생성
    items = [
        Item(350, 250, "food"),
        Item(450, 350, "medkit"),
        Item(250, 400, "food"),
        Item(520, 280, "food")
    ]
    
    font = pygame.font.SysFont('malgungothic', 20)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return
            
            # 아이템 줍기 (E키)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if survivor.alive:
                    for item in items:
                        if not item.picked and survivor.world_pos.distance_to(item.world_pos) < 40:
                            survivor.pickup_item(item)
                            item.picked = True
                            break

        # 업데이트
        survivor.update(house, zombies)
        for zombie in zombies:
            if survivor.alive:
                zombie.update(survivor.world_pos, house)
        
        # 카메라
        ix, iy = to_iso(survivor.world_pos.x, survivor.world_pos.y)
        cam_off = (WINDOW_WIDTH // 2 - ix, WINDOW_HEIGHT // 2 - iy)
        
        # 렌더링
        screen.fill(COLOR_BG)
        render_house(screen, house, cam_off)
        
        # 아이템
        for item in items:
            item.draw(screen, cam_off)
        
        # 캐릭터
        for zombie in zombies:
            zombie.draw(screen, cam_off)
        survivor.draw(screen, cam_off)
        
        # UI
        draw_ui(screen, survivor)
        
        # 조작법
        help_text = font.render("WASD: 이동 | E: 아이템 줍기 | 좀비 피하기!", True, (255, 255, 255))
        screen.blit(help_text, (WINDOW_WIDTH - 400, 20))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()