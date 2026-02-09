# -*- coding: utf-8 -*-
"""
아파트 - 통합 맵 시스템 (p008)
- 단일 2D 평면도로 전체 관리
- 카메라 기준 컬링
- Z-Order + 벽 뒤 캐릭터 시인성(반투명/실루엣)
- 폰트 폴백 (Linux 대비)
"""
import pygame
import math

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
FPS = 60
TILE_SIZE = 40

# 색상
COLOR_BG = (30, 30, 35)
COLOR_WALL = (160, 150, 140)
COLOR_WALL_TOP = (180, 170, 160)
COLOR_FLOOR_LIVING = (220, 210, 190)
COLOR_FLOOR_BEDROOM = (210, 200, 180)
COLOR_FLOOR_KITCHEN = (200, 190, 170)
COLOR_FLOOR_BATH = (240, 248, 255)
COLOR_FLOOR_BALCONY = (190, 190, 190)
COLOR_GRID = (180, 180, 180)
COLOR_DOOR = (139, 90, 60)
COLOR_DOOR_GLOW = (255, 200, 100)
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 203, 164)
WALL_H = 90
WALL_D = 15

def to_iso(x, y):
    return (x - y), (x + y) / 2


# ========== 통합 맵 (Single Map) ==========
# grid[ty][tx] = {"room_id": str, "room_name": str, "color": tuple} or None(벽/빈칸)
# 타일 좌표 (tx, ty) → 월드 픽셀 (tx*TILE_SIZE, ty*TILE_SIZE)

def build_unified_map():
    """설계도 기준: 현관(좌상), 주방(상중), 거실(중앙), 베란다(하중), 동쪽 방1·욕실·방2"""
    # 맵 크기 (타일 단위)
    MAP_TW = 28
    MAP_TH = 30
    grid = [[None] * MAP_TW for _ in range(MAP_TH)]
    room_names = {}

    def fill(tx0, ty0, tw, th, room_id, room_name, color):
        for ty in range(ty0, min(ty0 + th, MAP_TH)):
            for tx in range(tx0, min(tx0 + tw, MAP_TW)):
                if 0 <= ty < MAP_TH and 0 <= tx < MAP_TW:
                    grid[ty][tx] = {"room_id": room_id, "room_name": room_name, "color": color}
        room_names[room_id] = room_name

    # 설계도 배치 (타일 좌표)
    fill(0, 8, 4, 8, "entrance", "현관", COLOR_FLOOR_LIVING)
    fill(4, 0, 12, 6, "kitchen", "주방", COLOR_FLOOR_KITCHEN)
    fill(4, 6, 14, 12, "living", "거실", COLOR_FLOOR_LIVING)
    fill(6, 18, 6, 10, "balcony", "베란다", COLOR_FLOOR_BALCONY)
    fill(18, 0, 10, 10, "bedroom1", "침실1", COLOR_FLOOR_BEDROOM)
    fill(18, 10, 6, 8, "bathroom", "욕실", COLOR_FLOOR_BATH)
    fill(18, 18, 8, 8, "bedroom2", "침실2", COLOR_FLOOR_BEDROOM)

    return grid, room_names, MAP_TW, MAP_TH


def world_to_tile(wx, wy):
    tx = int(wx // TILE_SIZE)
    ty = int(wy // TILE_SIZE)
    return tx, ty


def is_walkable(grid, map_tw, map_th, wx, wy):
    tx, ty = world_to_tile(wx, wy)
    if tx < 0 or ty < 0 or tx >= map_tw or ty >= map_th:
        return False
    cell = grid[ty][tx]
    return cell is not None


def get_room_at(grid, map_tw, map_th, wx, wy):
    tx, ty = world_to_tile(wx, wy)
    if tx < 0 or ty < 0 or tx >= map_tw or ty >= map_th:
        return None
    cell = grid[ty][tx]
    return cell.get("room_name") if cell else None


# ========== 카메라 컬링 ==========
def get_visible_tile_bounds(cam_wx, cam_wy, map_tw, map_th, margin_tiles=4):
    """화면에 보이는 타일 범위 (여유 margin 포함). 월드 픽셀 cam = 캐릭터 위치 기준."""
    # 화면 크기만큼 + 여유분
    half_w = (WINDOW_WIDTH // 2) + margin_tiles * TILE_SIZE
    half_h = (WINDOW_HEIGHT // 2) + margin_tiles * TILE_SIZE
    tx_min = max(0, int((cam_wx - half_w) / TILE_SIZE))
    ty_min = max(0, int((cam_wy - half_h) / TILE_SIZE))
    tx_max = min(map_tw, int((cam_wx + half_w) / TILE_SIZE) + 2)
    ty_max = min(map_th, int((cam_wy + half_h) / TILE_SIZE) + 2)
    return tx_min, ty_min, tx_max, ty_max


# ========== 벽 정보 (Z-Order / 가림용) ==========
def collect_wall_segments(grid, map_tw, map_th, tx_min, ty_min, tx_max, ty_max):
    """지정 타일 범위 내에서 그릴 벽 세그먼트 수집. 각 벽에 depth(iso) 부여."""
    walls = []
    for ty in range(ty_min, ty_max):
        for tx in range(tx_min, tx_max):
            cell = grid[ty][tx] if 0 <= ty < map_th and 0 <= tx < map_tw else None
            wx = tx * TILE_SIZE
            wy = ty * TILE_SIZE
            depth = tx + ty  # iso depth
            # 북쪽 벽: 위쪽 타일이 없거나 다른 방
            north = grid[ty - 1][tx] if ty - 1 >= 0 else None
            if north is None or north.get("room_id") != (cell.get("room_id") if cell else None):
                if cell is not None:
                    b_iso = to_iso(wx, wy)
                    e_iso = to_iso(wx + TILE_SIZE, wy)
                    walls.append({
                        "pts": [b_iso, e_iso, (e_iso[0], e_iso[1] - WALL_H), (b_iso[0], b_iso[1] - WALL_H)],
                        "depth": depth,
                        "top_pts": [(b_iso[0], b_iso[1] - WALL_H), (e_iso[0], e_iso[1] - WALL_H),
                                    (e_iso[0], e_iso[1] - WALL_H - WALL_D), (b_iso[0], b_iso[1] - WALL_H - WALL_D)],
                    })
            # 서쪽 벽
            west = grid[ty][tx - 1] if tx - 1 >= 0 else None
            if west is None or west.get("room_id") != (cell.get("room_id") if cell else None):
                if cell is not None:
                    b_iso = to_iso(wx, wy)
                    e_iso = to_iso(wx, wy + TILE_SIZE)
                    walls.append({
                        "pts": [b_iso, e_iso, (e_iso[0], e_iso[1] - WALL_H), (b_iso[0], b_iso[1] - WALL_H)],
                        "depth": depth,
                        "top_pts": [(b_iso[0], b_iso[1] - WALL_H), (e_iso[0], e_iso[1] - WALL_H),
                                    (e_iso[0], e_iso[1] - WALL_H - WALL_D), (b_iso[0], b_iso[1] - WALL_H - WALL_D)],
                    })
    return walls


# ========== 캐릭터 클래스 (p007 유지, update만 통합 맵 대응) ==========
class Character:
    def __init__(self, x, y, role="father"):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        self.role = role

        if role == "father":
            self.limb_len, self.body_h, self.body_w = 20, 30, 22
            self.head_r = 14
            self.head_color, self.body_color = (255, 203, 164), (70, 130, 180)
            self.pants_color, self.hair_color = (40, 60, 80), (50, 40, 30)
            self.speed = 5
        elif role == "mother":
            self.limb_len, self.body_h, self.body_w = 18, 28, 20
            self.head_r = 13
            self.head_color, self.body_color = (255, 218, 185), (220, 120, 140)
            self.pants_color, self.hair_color = (60, 50, 70), (80, 50, 30)
            self.ponytail_color = (70, 45, 25)
            self.speed = 5
        elif role == "daughter":
            self.limb_len, self.body_h, self.body_w = 14, 20, 16
            self.head_r = 11
            self.head_color, self.body_color = (255, 228, 196), (255, 220, 100)
            self.pants_color, self.hair_color = (100, 150, 200), (40, 30, 20)
            self.ribbon_color = (255, 100, 150)
            self.speed = 5

    def update(self, target_pos=None, grid=None, map_tw=0, map_th=0):
        move_vec = pygame.Vector2(0, 0)
        if target_pos is None:
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
        else:
            diff = target_pos - self.world_pos
            if diff.length() > 65:
                move_vec = diff.normalize() * self.speed
                self.look_dir = pygame.Vector2(move_vec.x - move_vec.y, move_vec.x + move_vec.y).normalize()

        if move_vec.length() > 0 and grid is not None:
            self.walk_count += 0.2
            self.world_pos.x += move_vec.x
            if not is_walkable(grid, map_tw, map_th, self.world_pos.x, self.world_pos.y):
                self.world_pos.x -= move_vec.x
            self.world_pos.y += move_vec.y
            if not is_walkable(grid, map_tw, map_th, self.world_pos.x, self.world_pos.y):
                self.world_pos.y -= move_vec.y
        else:
            self.walk_count = 0

    def get_depth(self):
        return self.world_pos.x + self.world_pos.y

    def draw(self, surface, cam_off, force_silhouette=False):
        iso_p = to_iso(self.world_pos.x, self.world_pos.y)
        cx = iso_p[0] + cam_off[0]
        cy = iso_p[1] + cam_off[1]
        swing = math.sin(self.walk_count) * (self.limb_len / 2.5)
        bobbing = abs(math.sin(self.walk_count)) * 2.5
        pelvis_y = cy - self.limb_len
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        draw_w = self.body_w - 4 if is_side else self.body_w
        bag_w, bag_h = draw_w + 2, max(8, self.body_h - 12)
        bag_rect = (cx - bag_w // 2, pelvis_y - self.body_h + 8 + bobbing, bag_w, bag_h)
        pants_h = self.body_h // 2
        body_top = pelvis_y - pants_h
        shoulder_y = body_top - (self.body_h - pants_h) + 3
        head_y = shoulder_y - 8

        if force_silhouette:
            # 벽에 가려질 때 실루엣 (단색 + 테두리)
            silhouette_color = (60, 60, 80)
            pygame.draw.rect(surface, silhouette_color, (cx - draw_w // 2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h))
            pygame.draw.rect(surface, silhouette_color, (cx - draw_w // 2, pelvis_y - pants_h, draw_w, pants_h))
            pygame.draw.circle(surface, silhouette_color, (int(cx), int(head_y)), self.head_r)
            pygame.draw.circle(surface, (80, 80, 100), (int(cx), int(head_y)), self.head_r, 2)
            return

        if not is_back:
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        pygame.draw.rect(surface, self.pants_color, (cx - draw_w // 2, pelvis_y - pants_h, draw_w, pants_h))
        pygame.draw.line(surface, COLOR_LIMB, (cx - 4, pelvis_y), (cx - 4 - swing / 2, cy + swing / 2), 2)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 4, pelvis_y), (cx + 4 + swing / 2, cy - swing / 2), 2)
        pygame.draw.rect(surface, self.body_color, (cx - draw_w // 2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h))
        pygame.draw.rect(surface, (200, 200, 200), (cx - draw_w // 2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h), 1)
        if is_back:
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w // 2, shoulder_y), (cx - draw_w // 2 - 8, shoulder_y + 18 - swing), 2)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w // 2, shoulder_y), (cx + draw_w // 2 + 8, shoulder_y + 18 + swing), 2)
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)
        if self.role == "father":
            if not is_back:
                pygame.draw.ellipse(surface, self.hair_color, (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r))
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
        elif self.role == "mother":
            if not is_back:
                pygame.draw.ellipse(surface, self.hair_color, (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r + 2))
                if self.look_dir.y < 0.7:
                    px, py = cx - self.look_dir.x * 10 - 5, head_y + 4 - self.look_dir.y * 5
                    pygame.draw.ellipse(surface, self.ponytail_color, (px, py, 10, 16))
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
                pygame.draw.ellipse(surface, self.ponytail_color, (cx - 5, head_y + 6, 10, 18))
        elif self.role == "daughter":
            if not is_back:
                pygame.draw.ellipse(surface, self.hair_color, (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r))
                lx = cx - self.head_r - 3 - self.look_dir.x * 3
                ly = head_y + 2 - self.look_dir.y * 2
                pygame.draw.circle(surface, self.hair_color, (int(lx), int(ly)), 5)
                pygame.draw.circle(surface, self.ribbon_color, (int(lx), int(ly - 3)), 3)
                rx, ry = cx + self.head_r - 3 + self.look_dir.x * 3, head_y + 2 - self.look_dir.y * 2
                pygame.draw.circle(surface, self.hair_color, (int(rx), int(ry)), 5)
                pygame.draw.circle(surface, self.ribbon_color, (int(rx), int(ry - 3)), 3)
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
                for ox in (-self.head_r - 2, self.head_r + 2):
                    pygame.draw.circle(surface, self.hair_color, (int(cx + ox), int(head_y + 4)), 4)
        pygame.draw.circle(surface, (220, 220, 220), (int(cx), int(head_y)), self.head_r, 1)
        if not is_back:
            ex, ey = cx + self.look_dir.x * 3, head_y + self.look_dir.y * 1.5
            for dx in (-4, 4):
                pygame.draw.circle(surface, (255, 255, 255), (int(ex + dx), int(ey)), 3)
                pygame.draw.circle(surface, (50, 50, 50), (int(ex + dx), int(ey)), 2)


# 컬링 + Z-Order + 벽 반투명 / 가려진 캐릭터 실루엣
def render_unified_v2(screen, grid, map_tw, map_th, characters, cam_off, cam_wx, cam_wy):
    screen.fill(COLOR_BG)
    tx_min, ty_min, tx_max, ty_max = get_visible_tile_bounds(cam_wx, cam_wy, map_tw, map_th)

    # 1) 바닥 (카메라 컬링)
    for ty in range(ty_min, ty_max):
        for tx in range(tx_min, tx_max):
            if ty < 0 or tx < 0 or ty >= map_th or tx >= map_tw:
                continue
            cell = grid[ty][tx]
            if cell is None:
                continue
            wx, wy = tx * TILE_SIZE, ty * TILE_SIZE
            ix, iy = to_iso(wx, wy)
            pts = [
                (ix + cam_off[0], iy + cam_off[1]),
                (ix + TILE_SIZE + cam_off[0], iy + TILE_SIZE / 2 + cam_off[1]),
                (ix + cam_off[0], iy + TILE_SIZE + cam_off[1]),
                (ix - TILE_SIZE + cam_off[0], iy + TILE_SIZE / 2 + cam_off[1]),
            ]
            pygame.draw.polygon(screen, cell["color"], pts)
            pygame.draw.polygon(screen, COLOR_GRID, pts, 1)

    walls = collect_wall_segments(grid, map_tw, map_th, tx_min, ty_min, tx_max, ty_max)
    walls_sorted = sorted(walls, key=lambda w: w["depth"])
    chars_sorted = sorted(characters, key=lambda c: c.get_depth())

    # 2) Z-Order: depth 순으로 벽·캐릭터 교차. 가리는 벽은 반투명, 가려진 캐릭터는 실루엣
    all_items = [(w["depth"], "wall", w) for w in walls_sorted] + [(c.get_depth(), "char", c) for c in chars_sorted]
    all_items.sort(key=lambda x: x[0])
    drawn_chars = set()

    for depth, kind, obj in all_items:
        if kind == "wall":
            w = obj
            pts = [(p[0] + cam_off[0], p[1] + cam_off[1]) for p in w["pts"]]
            top_pts = [(p[0] + cam_off[0], p[1] + cam_off[1]) for p in w["top_pts"]]
            for c in chars_sorted:
                if c.get_depth() < depth and id(c) not in drawn_chars:
                    c.draw(screen, cam_off, force_silhouette=True)
                    drawn_chars.add(id(c))
            occludes = any(c.get_depth() < depth for c in chars_sorted)
            if occludes:
                surf = pygame.Surface((WINDOW_WIDTH + 400, WINDOW_HEIGHT + 400))
                surf.set_colorkey((1, 1, 1))
                surf.fill((1, 1, 1))
                off = (200 - cam_off[0], 200 - cam_off[1])
                pygame.draw.polygon(surf, COLOR_WALL, [(p[0] + off[0], p[1] + off[1]) for p in w["pts"]])
                pygame.draw.polygon(surf, COLOR_WALL_TOP, [(p[0] + off[0], p[1] + off[1]) for p in w["top_pts"]])
                surf.set_alpha(160)
                screen.blit(surf, (-200, -200))
            else:
                pygame.draw.polygon(screen, COLOR_WALL, pts)
                pygame.draw.polygon(screen, COLOR_WALL_TOP, top_pts)
        else:
            c = obj
            if id(c) not in drawn_chars:
                in_front = any(w["depth"] > c.get_depth() for w in walls_sorted)
                c.draw(screen, cam_off, force_silhouette=in_front)
                drawn_chars.add(id(c))

    # 3) 벽에 가려지지 않은 캐릭터만 일반 그리기로 한 번 더 (앞에 나오도록)
    for c in chars_sorted:
        if not any(w["depth"] > c.get_depth() for w in walls_sorted):
            c.draw(screen, cam_off, force_silhouette=False)


# ========== 메인 ==========
def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("아파트 - 통합 맵 (단일 평면도)")
    clock = pygame.time.Clock()

    grid, room_names, MAP_TW, MAP_TH = build_unified_map()

    # 캐릭터 시작: 거실 중앙 (타일 4+7, 6+6 등)
    start_wx = (4 + 7) * TILE_SIZE + TILE_SIZE // 2
    start_wy = (6 + 6) * TILE_SIZE + TILE_SIZE // 2
    father = Character(start_wx, start_wy, "father")
    mother = Character(start_wx - 40, start_wy - 40, "mother")
    daughter = Character(start_wx - 80, start_wy - 80, "daughter")
    characters = [daughter, mother, father]

    try:
        font = pygame.font.SysFont("malgungothic", 28)
    except Exception:
        try:
            font = pygame.font.SysFont("nanumgothic", 28)
        except Exception:
            font = pygame.font.SysFont(None, 28)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        father.update(grid=grid, map_tw=MAP_TW, map_th=MAP_TH)
        mother.update(father.world_pos, grid=grid, map_tw=MAP_TW, map_th=MAP_TH)
        daughter.update(mother.world_pos, grid=grid, map_tw=MAP_TW, map_th=MAP_TH)

        cam_wx = father.world_pos.x
        cam_wy = father.world_pos.y
        ix, iy = to_iso(cam_wx, cam_wy)
        cam_off = (WINDOW_WIDTH // 2 - ix, WINDOW_HEIGHT // 2 - iy)

        render_unified_v2(screen, grid, MAP_TW, MAP_TH, characters, cam_off, cam_wx, cam_wy)

        room_name = get_room_at(grid, MAP_TW, MAP_TH, father.world_pos.x, father.world_pos.y) or "?"
        text = font.render(f"{room_name} | WASD: 이동 | 통합 맵", True, (255, 255, 255))
        text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
        text_bg.fill((0, 0, 0))
        text_bg.set_alpha(180)
        screen.blit(text_bg, (10, 10))
        screen.blit(text, (20, 15))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
