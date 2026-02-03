import pygame
import math

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
info = pygame.display.Info()
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h

FPS = 60
TILE_SIZE = 40

# 색상 정의
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

def to_iso(x, y):
    return (x - y), (x + y) / 2

# --- 독립 맵 클래스 ---
class IndependentRoom:
    def __init__(self, name, width, height, floor_color):
        self.name = name
        self.origin_x = 3
        self.origin_y = 3
        self.tw = width   # 타일 너비
        self.th = height  # 타일 높이
        self.floor_color = floor_color
        self.wall_h = 90
        self.wall_d = 15
        self.doors = []  # 문 리스트
    
    def add_door(self, x, y, to_map, to_x, to_y, label="문"):
        """문 추가 (타일 좌표)"""
        self.doors.append({
            "x": x,
            "y": y,
            "to_map": to_map,    # 연결될 맵 이름
            "to_x": to_x,        # 도착 위치 x
            "to_y": to_y,        # 도착 위치 y
            "label": label
        })
    
    def get_floor_rect(self):
        """이동 가능 영역"""
        return pygame.Rect(
            (self.origin_x + 0.5) * TILE_SIZE,
            (self.origin_y + 0.5) * TILE_SIZE,
            (self.tw - 1) * TILE_SIZE,
            (self.th - 1) * TILE_SIZE
        )
    
    def check_door_collision(self, pos):
        """문 충돌 체크"""
        for door in self.doors:
            dx = (self.origin_x + door["x"]) * TILE_SIZE
            dy = (self.origin_y + door["y"]) * TILE_SIZE
            door_rect = pygame.Rect(dx - 20, dy - 20, 40, 40)
            if door_rect.collidepoint(pos.x, pos.y):
                return door
        return None

# --- 캐릭터 클래스 (수정 금지!) ---
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
            walkable = room.get_floor_rect()
            
            self.world_pos.x += move_vec.x
            if not walkable.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.x -= move_vec.x
            
            self.world_pos.y += move_vec.y
            if not walkable.collidepoint(self.world_pos.x, self.world_pos.y):
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
        
        pygame.draw.line(surface, COLOR_LIMB, (cx - 4, pelvis_y), (cx - 4 - swing/2, cy + swing/2), 2)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 4, pelvis_y), (cx + 4 + swing/2, cy - swing/2), 2)
        
        body_top = pelvis_y - pants_h
        body_rect = (cx - draw_w//2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h)
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (200, 200, 200), body_rect, 1)
        
        if is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        shoulder_y = body_top - (self.body_h - pants_h) + 3
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y), 
                        (cx - draw_w//2 - 8, shoulder_y + 18 - swing), 2)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y), 
                        (cx + draw_w//2 + 8, shoulder_y + 18 + swing), 2)
        
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

# --- 렌더링 ---
def render_room(screen, room, characters, cam_off):
    screen.fill(COLOR_BG)
    
    # 1. 바닥
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
            pygame.draw.polygon(screen, room.floor_color, pts)
            pygame.draw.polygon(screen, COLOR_GRID, pts, 1)
    
    # 2. 북쪽 벽
    bx = room.origin_x * TILE_SIZE
    by = room.origin_y * TILE_SIZE
    ex = (room.origin_x + room.tw) * TILE_SIZE
    ey = room.origin_y * TILE_SIZE
    b_iso = to_iso(bx, by)
    e_iso = to_iso(ex, ey)
    
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)
    
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
    
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)
    
    top_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h - room.wall_d + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h - room.wall_d + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL_TOP, top_pts)
    
    # 4. 문 그리기
    for door in room.doors:
        dx = (room.origin_x + door["x"]) * TILE_SIZE
        dy = (room.origin_y + door["y"]) * TILE_SIZE
        iso_d = to_iso(dx, dy)
        
        # 문 빛 효과
        pygame.draw.circle(screen, COLOR_DOOR_GLOW, 
                          (int(iso_d[0] + cam_off[0]), int(iso_d[1] + cam_off[1])), 25)
        # 문
        door_rect = pygame.Rect(iso_d[0] + cam_off[0] - 20, iso_d[1] + cam_off[1] - 20, 40, 40)
        pygame.draw.rect(screen, COLOR_DOOR, door_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 60, 30), door_rect, 3, border_radius=8)
    
    # 5. 캐릭터
    for char in characters:
        char.draw(screen, cam_off)

# --- 메인 ---
def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("아파트 - 독립 맵 시스템")
    clock = pygame.time.Clock()
    
    # 맵 생성
    rooms = {}
    
    # 주방 및 식당 (중앙 허브)
    rooms["kitchen"] = IndependentRoom("주방 및 식당", 12, 10, COLOR_FLOOR_KITCHEN)
    rooms["kitchen"].add_door(2, 0, "bedroom1", 6, 8, "침실1로")
    rooms["kitchen"].add_door(6, 0, "bathroom", 3, 8, "욕실로")
    rooms["kitchen"].add_door(10, 0, "bedroom2", 4, 8, "침실2로")
    rooms["kitchen"].add_door(0, 5, "living", 11, 5, "거실로")
    rooms["kitchen"].add_door(11, 5, "living", 0, 5, "거실로")
    rooms["kitchen"].add_door(6, 9, "entrance", 3, 1, "현관으로")
    
    # 침실1
    rooms["bedroom1"] = IndependentRoom("침실1", 10, 8, COLOR_FLOOR_BEDROOM)
    rooms["bedroom1"].add_door(6, 8, "kitchen", 2, 1, "주방으로")
    
    # 욕실
    rooms["bathroom"] = IndependentRoom("욕실", 6, 8, COLOR_FLOOR_BATH)
    rooms["bathroom"].add_door(3, 8, "kitchen", 6, 1, "주방으로")
    
    # 침실2
    rooms["bedroom2"] = IndependentRoom("침실2", 10, 8, COLOR_FLOOR_BEDROOM)
    rooms["bedroom2"].add_door(4, 8, "kitchen", 10, 1, "주방으로")
    rooms["bedroom2"].add_door(9, 4, "balcony", 1, 4, "발코니로")
    
    # 거실
    rooms["living"] = IndependentRoom("거실", 12, 10, COLOR_FLOOR_LIVING)
    rooms["living"].add_door(0, 5, "kitchen", 11, 5, "주방으로")
    rooms["living"].add_door(11, 5, "kitchen", 1, 5, "주방으로")
    rooms["living"].add_door(11, 8, "balcony", 1, 6, "발코니로")
    rooms["living"].add_door(0, 3, "entrance", 7, 2, "현관으로")
    
    # 발코니
    rooms["balcony"] = IndependentRoom("발코니", 6, 10, COLOR_FLOOR_BALCONY)
    rooms["balcony"].add_door(0, 4, "bedroom2", 9, 4, "침실2로")
    rooms["balcony"].add_door(0, 6, "living", 11, 8, "거실로")
    
    # 현관
    rooms["entrance"] = IndependentRoom("현관", 8, 6, COLOR_FLOOR_LIVING)
    rooms["entrance"].add_door(3, 0, "kitchen", 6, 9, "주방으로")
    rooms["entrance"].add_door(7, 2, "living", 0, 3, "거실로")
    
    # 현재 맵
    current_room_name = "kitchen"
    current_room = rooms[current_room_name]
    
    # 캐릭터
    father = Character(250, 250, "father")
    mother = Character(210, 210, "mother")
    daughter = Character(170, 170, "daughter")
    characters = [daughter, mother, father]
    
    font = pygame.font.SysFont('malgungothic', 28)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return

        father.update(room=current_room)
        mother.update(father.world_pos, current_room)
        daughter.update(mother.world_pos, current_room)
        
        # 문 충돌 체크
        door = current_room.check_door_collision(father.world_pos)
        if door:
            # 맵 전환
            current_room_name = door["to_map"]
            current_room = rooms[current_room_name]
            
            # 문 위치(월드)
            new_x = (current_room.origin_x + door["to_x"]) * TILE_SIZE
            new_y = (current_room.origin_y + door["to_y"]) * TILE_SIZE
            walkable = current_room.get_floor_rect()
            
            # 방 안쪽 방향: 문 → 방 중심
            room_center_x = (current_room.origin_x + current_room.tw / 2) * TILE_SIZE
            room_center_y = (current_room.origin_y + current_room.th / 2) * TILE_SIZE
            dir_x = room_center_x - new_x
            dir_y = room_center_y - new_y
            length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
            if length < 1:
                dir_x, dir_y = 0, 1
            else:
                dir_x, dir_y = dir_x / length, dir_y / length
            
            # 아버지: 문 위치 → 바닥 안으로 클램프
            father.world_pos = pygame.Vector2(new_x, new_y)
            fx = max(walkable.x, min(walkable.x + walkable.w, father.world_pos.x))
            fy = max(walkable.y, min(walkable.y + walkable.h, father.world_pos.y))
            father.world_pos = pygame.Vector2(fx, fy)
            
            # 엄마·딸: 아버지 뒤쪽(방 안쪽)에 배치 후 클램프
            mother.world_pos = pygame.Vector2(fx + dir_x * 50, fy + dir_y * 50)
            mother.world_pos.x = max(walkable.x, min(walkable.x + walkable.w, mother.world_pos.x))
            mother.world_pos.y = max(walkable.y, min(walkable.y + walkable.h, mother.world_pos.y))
            
            daughter.world_pos = pygame.Vector2(fx + dir_x * 100, fy + dir_y * 100)
            daughter.world_pos.x = max(walkable.x, min(walkable.x + walkable.w, daughter.world_pos.x))
            daughter.world_pos.y = max(walkable.y, min(walkable.y + walkable.h, daughter.world_pos.y))
        
        # 카메라
        ix, iy = to_iso(father.world_pos.x, father.world_pos.y)
        cam_off = (WINDOW_WIDTH // 2 - ix, WINDOW_HEIGHT // 2 - iy)
        
        render_room(screen, current_room, characters, cam_off)
        
        # UI
        text = font.render(f"{current_room.name} | WASD: 이동 | 문: 노란 빛", True, (255, 255, 255))
        text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
        text_bg.fill((0, 0, 0))
        text_bg.set_alpha(180)
        screen.blit(text_bg, (10, 10))
        screen.blit(text, (20, 15))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()