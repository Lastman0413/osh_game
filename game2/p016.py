import pygame
import math

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
info = pygame.display.Info()
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h

FPS = 60
TILE_SIZE = 40

# 색상 정의 (미니 팔레트)
COLOR_BG = (30, 30, 35)
COLOR_WALL = (160, 150, 140)
COLOR_WALL_TOP = (180, 170, 160)
COLOR_FLOOR = (220, 210, 190)
COLOR_GRID = (200, 200, 200)
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 203, 164)

def to_iso(x, y):
    """월드 좌표를 아이소메트릭 좌표로 변환"""
    return (x - y), (x + y) / 2

# --- 방 클래스 (미니 방식) ---
class Room:
    def __init__(self):
        self.origin_x = 5
        self.origin_y = 5
        self.tw = 12  # 타일 너비
        self.th = 10  # 타일 높이
        self.wall_h = 90   # 벽 높이
        self.wall_d = 15   # 벽 두께

    def get_floor_rect(self):
        """충돌 계산용 바닥 범위"""
        return pygame.Rect(
            self.origin_x * TILE_SIZE + 10,
            self.origin_y * TILE_SIZE + 10,
            self.tw * TILE_SIZE - 20,
            self.th * TILE_SIZE - 20
        )

# --- 캐릭터 클래스 (우디 버전) ---
class Character:
    def __init__(self, x, y, role="father"):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        self.role = role
        
        if role == "father":
            self.limb_len = 20
            self.body_h = 30
            self.body_w = 22
            self.head_r = 14
            self.head_color = (255, 203, 164)
            self.body_color = (70, 130, 180)
            self.pants_color = (40, 60, 80)
            self.hair_color = (50, 40, 30)
            self.speed = 5
        elif role == "mother":
            self.limb_len = 18
            self.body_h = 28
            self.body_w = 20
            self.head_r = 13
            self.head_color = (255, 218, 185)
            self.body_color = (220, 120, 140)
            self.pants_color = (60, 50, 70)
            self.hair_color = (80, 50, 30)
            self.ponytail_color = (70, 45, 25)
            self.speed = 5
        elif role == "daughter":
            self.limb_len = 14
            self.body_h = 20
            self.body_w = 16
            self.head_r = 11
            self.head_color = (255, 228, 196)
            self.body_color = (255, 220, 100)
            self.pants_color = (100, 150, 200)
            self.hair_color = (40, 30, 20)
            self.ribbon_color = (255, 100, 150)
            self.speed = 5

    def update(self, target_pos=None, room=None):
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

        if move_vec.length() > 0:
            self.walk_count += 0.2
            floor_rect = room.get_floor_rect()
            
            # X축 충돌 체크 (미니 방식)
            self.world_pos.x += move_vec.x
            if not floor_rect.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.x -= move_vec.x
            
            # Y축 충돌 체크
            self.world_pos.y += move_vec.y
            if not floor_rect.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.y -= move_vec.y
        else:
            self.walk_count = 0

    def draw(self, surface, cam_off):
        iso_p = to_iso(self.world_pos.x, self.world_pos.y)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
        
        swing = math.sin(self.walk_count) * (self.limb_len / 2.5)
        bobbing = abs(math.sin(self.walk_count)) * 2.5
        pelvis_y = cy - self.limb_len
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        draw_w = self.body_w - 4 if is_side else self.body_w
        
        bag_w = draw_w + 2
        bag_h = max(8, self.body_h - 12)
        bag_rect = (cx - bag_w//2, pelvis_y - self.body_h + 8 + bobbing, bag_w, bag_h)
        if not is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        pants_h = self.body_h // 2
        pants_rect = (cx - draw_w//2, pelvis_y - pants_h, draw_w, pants_h)
        pygame.draw.rect(surface, self.pants_color, pants_rect)
        
        leg_thickness = 2
        pygame.draw.line(surface, COLOR_LIMB, (cx - 4, pelvis_y), (cx - 4 - swing/2, cy + swing/2), leg_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 4, pelvis_y), (cx + 4 + swing/2, cy - swing/2), leg_thickness)
        
        body_top = pelvis_y - pants_h
        body_rect = (cx - draw_w//2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h)
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (200, 200, 200), body_rect, 1)
        
        if is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        shoulder_y = body_top - (self.body_h - pants_h) + 3
        arm_thickness = 2
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y), 
                        (cx - draw_w//2 - 8, shoulder_y + 18 - swing), arm_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y), 
                        (cx + draw_w//2 + 8, shoulder_y + 18 + swing), arm_thickness)
        
        head_y = shoulder_y - 8
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)
        
        if self.role == "father":
            if not is_back:
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
        
        elif self.role == "mother":
            if not is_back:
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r + 2)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
                if self.look_dir.y < 0.7:
                    ponytail_offset_x = -self.look_dir.x * 10
                    ponytail_offset_y = -self.look_dir.y * 5
                    ponytail_x = cx + ponytail_offset_x - 5
                    ponytail_y = head_y + 4 + ponytail_offset_y
                    pygame.draw.ellipse(surface, self.ponytail_color, (ponytail_x, ponytail_y, 10, 16))
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
                ponytail_x = cx - 5
                ponytail_y = head_y + 6
                pygame.draw.ellipse(surface, self.ponytail_color, (ponytail_x, ponytail_y, 10, 18))
        
        elif self.role == "daughter":
            if not is_back:
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
                pigtail_base_y = head_y + 2
                left_depth = -self.look_dir.x * 3
                left_pigtail_x = cx - self.head_r - 3 + left_depth
                left_pigtail_y = pigtail_base_y - self.look_dir.y * 2
                pygame.draw.circle(surface, self.hair_color, (int(left_pigtail_x), int(left_pigtail_y)), 5)
                pygame.draw.circle(surface, self.ribbon_color, (int(left_pigtail_x), int(left_pigtail_y - 3)), 3)
                right_depth = self.look_dir.x * 3
                right_pigtail_x = cx + self.head_r - 3 + right_depth
                right_pigtail_y = pigtail_base_y - self.look_dir.y * 2
                pygame.draw.circle(surface, self.hair_color, (int(right_pigtail_x), int(right_pigtail_y)), 5)
                pygame.draw.circle(surface, self.ribbon_color, (int(right_pigtail_x), int(right_pigtail_y - 3)), 3)
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
                left_pigtail_x = cx - self.head_r - 2
                right_pigtail_x = cx + self.head_r + 2
                pigtail_y = head_y + 4
                pygame.draw.circle(surface, self.hair_color, (int(left_pigtail_x), int(pigtail_y)), 4)
                pygame.draw.circle(surface, self.hair_color, (int(right_pigtail_x), int(pigtail_y)), 4)
        
        pygame.draw.circle(surface, (220, 220, 220), (int(cx), int(head_y)), self.head_r, 1)
        
        if not is_back:
            eye_x, eye_y = cx + self.look_dir.x * 3, head_y + self.look_dir.y * 1.5
            eye_spacing = 4
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x - eye_spacing), int(eye_y)), 3)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x + eye_spacing), int(eye_y)), 3)
            pygame.draw.circle(surface, (50, 50, 50), (int(eye_x - eye_spacing), int(eye_y)), 2)
            pygame.draw.circle(surface, (50, 50, 50), (int(eye_x + eye_spacing), int(eye_y)), 2)

# --- 렌더링 (미니 방식) ---
def render_game(screen, room, characters, cam_off):
    screen.fill(COLOR_BG)
    
    # 1. 바닥 그리기
    for tx in range(room.tw):
        for ty in range(room.th):
            wx = (room.origin_x + tx) * TILE_SIZE
            wy = (room.origin_y + ty) * TILE_SIZE
            ix, iy = to_iso(wx, wy)
            
            pts = [
                (ix + cam_off[0], iy + cam_off[1]),
                (ix + TILE_SIZE + cam_off[0], iy + TILE_SIZE/2 + cam_off[1]),
                (ix + cam_off[0], iy + TILE_SIZE + cam_off[1]),
                (ix - TILE_SIZE + cam_off[0], iy + TILE_SIZE/2 + cam_off[1])
            ]
            pygame.draw.polygon(screen, COLOR_FLOOR, pts)
            pygame.draw.polygon(screen, COLOR_GRID, pts, 1)

    # 2. 북쪽 벽
    bx = room.origin_x * TILE_SIZE
    by = room.origin_y * TILE_SIZE
    ex = (room.origin_x + room.tw) * TILE_SIZE
    ey = room.origin_y * TILE_SIZE
    b_iso = to_iso(bx, by)
    e_iso = to_iso(ex, ey)
    
    # 벽면
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)
    
    # 벽 윗면
    top_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h - room.wall_d + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h - room.wall_d + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL_TOP, top_pts)

    # 3. 서쪽 벽
    bx = room.origin_x * TILE_SIZE
    by = room.origin_y * TILE_SIZE
    ex = room.origin_x * TILE_SIZE
    ey = (room.origin_y + room.th) * TILE_SIZE
    b_iso = to_iso(bx, by)
    e_iso = to_iso(ex, ey)
    
    # 벽면
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)
    
    # 벽 윗면
    top_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h - room.wall_d + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h - room.wall_d + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL_TOP, top_pts)
    
    # 4. 캐릭터 그리기
    for char in characters:
        char.draw(screen, cam_off)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("미니 방 + 우디 캐릭터")
    clock = pygame.time.Clock()
    is_fullscreen = False
    cur_w, cur_h = WINDOW_WIDTH, WINDOW_HEIGHT
    
    room = Room()
    father = Character(400, 400, "father")
    mother = Character(360, 360, "mother")
    daughter = Character(320, 320, "daughter")
    
    characters = [daughter, mother, father]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
                    cur_w, cur_h = FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT
                else:
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    cur_w, cur_h = WINDOW_WIDTH, WINDOW_HEIGHT

        father.update(room=room)
        mother.update(father.world_pos, room)
        daughter.update(mother.world_pos, room)
        
        # 카메라
        ix, iy = to_iso(father.world_pos.x, father.world_pos.y)
        cam_off = (cur_w // 2 - ix, cur_h // 2 - iy)
        
        render_game(screen, room, characters, cam_off)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()