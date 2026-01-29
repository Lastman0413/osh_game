import pygame
import math

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
info = pygame.display.Info()
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h

FPS = 60
TILE_SIZE = 40  # 타일 크기 축소 (실내용)
MAP_WIDTH = 30   # 넓은 아파트
MAP_HEIGHT = 20  # 적당한 깊이
MAP_LIMIT_X = TILE_SIZE * MAP_WIDTH
MAP_LIMIT_Y = TILE_SIZE * MAP_HEIGHT

# 색상 정의
COLOR_WALL = (180, 160, 140)       # 벽 (베이지)
COLOR_FLOOR = (220, 210, 190)      # 마룻바닥
COLOR_DOOR = (139, 90, 60)         # 문 (갈색)
COLOR_WINDOW = (173, 216, 230)     # 창문 (하늘색)
COLOR_FURNITURE = (160, 82, 45)    # 가구 (갈색)
COLOR_BED = (255, 182, 193)        # 침대 (분홍)
COLOR_BATHROOM = (240, 248, 255)   # 욕실 타일
COLOR_BALCONY = (200, 200, 200)    # 베란다 바닥
COLOR_OUTSIDE = (255, 255, 255)    # 맵 외부
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 203, 164)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

# 아파트 구조 정의 (타일 단위)
# 0: 바닥, 1: 벽, 2: 문, 3: 창문, 4: 가구
class ApartmentMap:
    def __init__(self):
        # 방 영역 정의 (x, y, width, height, 타입)
        self.rooms = [
            # 거실 (중앙-왼쪽)
            {"x": 3, "y": 6, "w": 10, "h": 8, "type": "living", "name": "거실"},
            # 주방 (거실 위쪽)
            {"x": 3, "y": 3, "w": 6, "h": 3, "type": "kitchen", "name": "주방"},
            # 안방 (오른쪽 위)
            {"x": 15, "y": 3, "w": 8, "h": 6, "type": "master", "name": "안방"},
            # 작은방1 (오른쪽 중간)
            {"x": 15, "y": 10, "w": 6, "h": 5, "type": "room1", "name": "딸방"},
            # 작은방2 (오른쪽 아래)
            {"x": 15, "y": 16, "w": 6, "h": 4, "type": "room2", "name": "서재"},
            # 욕실1 (안방 옆)
            {"x": 24, "y": 3, "w": 4, "h": 4, "type": "bath1", "name": "욕실1"},
            # 욕실2 (복도)
            {"x": 13, "y": 12, "w": 2, "h": 3, "type": "bath2", "name": "욕실2"},
            # 베란다 (거실 왼쪽)
            {"x": 0, "y": 8, "w": 3, "h": 4, "type": "balcony", "name": "베란다"},
            # 현관 (아래쪽)
            {"x": 8, "y": 15, "w": 4, "h": 4, "type": "entrance", "name": "현관"},
        ]
        
        # 가구 배치 (x, y, w, h, color, 이름)
        self.furniture = [
            # 거실
            {"x": 160, "y": 320, "w": 120, "h": 60, "color": COLOR_FURNITURE, "name": "소파"},
            {"x": 200, "y": 400, "w": 60, "h": 60, "color": (100, 80, 60), "name": "테이블"},
            # 안방
            {"x": 680, "y": 180, "w": 80, "h": 100, "color": COLOR_BED, "name": "침대"},
            {"x": 900, "y": 160, "w": 40, "h": 60, "color": COLOR_FURNITURE, "name": "옷장"},
            # 딸방
            {"x": 660, "y": 440, "w": 60, "h": 80, "color": (255, 200, 220), "name": "침대"},
            {"x": 760, "y": 460, "w": 60, "h": 40, "color": COLOR_FURNITURE, "name": "책상"},
        ]
        
        # 문 위치 (x, y, direction: 'h'=가로, 'v'=세로)
        self.doors = [
            {"x": 480, "y": 600, "dir": "h", "name": "현관문"},  # 현관문 (출구)
            {"x": 600, "y": 360, "dir": "v", "name": "안방문"},
            {"x": 600, "y": 480, "dir": "v", "name": "딸방문"},
            {"x": 600, "y": 640, "dir": "v", "name": "서재문"},
        ]

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
            self.speed = 5  # 실내라 느리게
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

    def update(self, target_pos=None):
        if target_pos is None:
            keys = pygame.key.get_pressed()
            screen_move = pygame.Vector2(0, 0)
            if keys[pygame.K_w]: screen_move.y -= 1
            if keys[pygame.K_s]: screen_move.y += 1
            if keys[pygame.K_a]: screen_move.x -= 1
            if keys[pygame.K_d]: screen_move.x += 1
            
            if screen_move.length() > 0:
                screen_move = screen_move.normalize()
                world_move = pygame.Vector2(screen_move.x + screen_move.y, -screen_move.x + screen_move.y).normalize()
                self.look_dir = screen_move
                self.world_pos += world_move * self.speed
                self.walk_count += 0.2
            else: self.walk_count = 0
        else:
            dist_vec = target_pos - self.world_pos
            if dist_vec.length() > 65:
                move_dir = dist_vec.normalize()
                self.look_dir = pygame.Vector2(move_dir.x - move_dir.y, move_dir.x + move_dir.y).normalize()
                self.world_pos += move_dir * self.speed
                self.walk_count += 0.2
            else: self.walk_count = 0

        self.world_pos.x = max(0, min(self.world_pos.x, MAP_LIMIT_X))
        self.world_pos.y = max(0, min(self.world_pos.y, MAP_LIMIT_Y))

    def draw(self, surface, cam_off):
        iso_p = (self.world_pos.x - self.world_pos.y, (self.world_pos.x + self.world_pos.y) / 2)
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

def draw_apartment_map(surface, apt_map, cam_off, cur_w, cur_h):
    """아파트 맵 렌더링"""
    # 바닥 전체 그리기
    for x in range(0, MAP_LIMIT_X, TILE_SIZE):
        for y in range(0, MAP_LIMIT_Y, TILE_SIZE):
            p = (x - y, (x + y) / 2)
            if -150 < p[0] + cam_off[0] < cur_w + 150 and -150 < p[1] + cam_off[1] < cur_h + 150:
                pts = [(p[0]+cam_off[0], p[1]+cam_off[1]) for p in [
                    (x-y, (x+y)/2), 
                    (x+TILE_SIZE-y, (x+TILE_SIZE+y)/2), 
                    (x+TILE_SIZE-(y+TILE_SIZE), (x+TILE_SIZE+y+TILE_SIZE)/2), 
                    (x-(y+TILE_SIZE), (x+y+TILE_SIZE)/2)
                ]]
                
                # 방 타입에 따라 색상 다르게
                room_color = COLOR_FLOOR
                for room in apt_map.rooms:
                    rx, ry = room["x"] * TILE_SIZE, room["y"] * TILE_SIZE
                    if rx <= x < rx + room["w"] * TILE_SIZE and ry <= y < ry + room["h"] * TILE_SIZE:
                        if room["type"] == "bathroom" or room["type"] == "bath1" or room["type"] == "bath2":
                            room_color = COLOR_BATHROOM
                        elif room["type"] == "balcony":
                            room_color = COLOR_BALCONY
                        break
                
                pygame.draw.polygon(surface, room_color, pts)
                pygame.draw.polygon(surface, (200, 200, 200), pts, 1)
    
    # 벽 그리기 (방 테두리)
    for room in apt_map.rooms:
        rx = room["x"] * TILE_SIZE - room["y"] * TILE_SIZE
        ry = (room["x"] * TILE_SIZE + room["y"] * TILE_SIZE) / 2
        rw = room["w"] * TILE_SIZE
        rh = room["h"] * TILE_SIZE
        
        # 아이소메트릭 벽 (두꺼운 선)
        wall_pts = [
            (rx + cam_off[0], ry + cam_off[1]),
            (rx + rw + cam_off[0], ry + rw/2 + cam_off[1]),
            (rx + rw - rh + cam_off[0], ry + rw/2 + rh/2 + cam_off[1]),
            (rx - rh + cam_off[0], ry + rh/2 + cam_off[1])
        ]
        pygame.draw.lines(surface, COLOR_WALL, True, wall_pts, 4)
    
    # 가구 그리기
    for furn in apt_map.furniture:
        fx, fy = furn["x"], furn["y"]
        fw, fh = furn["w"], furn["h"]
        iso_fx = fx - fy
        iso_fy = (fx + fy) / 2
        
        furn_rect = pygame.Rect(iso_fx + cam_off[0] - fw//2, iso_fy + cam_off[1] - fh//2, fw, fh)
        pygame.draw.rect(surface, furn["color"], furn_rect, border_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), furn_rect, 2, border_radius=4)
    
    # 문 그리기
    for door in apt_map.doors:
        dx, dy = door["x"], door["y"]
        iso_dx = dx - dy
        iso_dy = (dx + dy) / 2
        
        if door["dir"] == "h":
            door_rect = pygame.Rect(iso_dx + cam_off[0] - 30, iso_dy + cam_off[1] - 5, 60, 10)
        else:
            door_rect = pygame.Rect(iso_dx + cam_off[0] - 5, iso_dy + cam_off[1] - 30, 10, 60)
        
        pygame.draw.rect(surface, COLOR_DOOR, door_rect, border_radius=2)
        pygame.draw.rect(surface, (100, 60, 30), door_rect, 2, border_radius=2)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("맵001 - 아파트 7층")
    clock = pygame.time.Clock()
    is_fullscreen = False
    cur_w, cur_h = WINDOW_WIDTH, WINDOW_HEIGHT
    
    # 아파트 맵
    apt_map = ApartmentMap()
    
    # 캐릭터 시작 위치 (거실)
    father = Character(400, 400, "father")
    mother = Character(360, 360, "mother")
    daughter = Character(320, 320, "daughter")
    
    font = pygame.font.Font(None, 32)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
                        cur_w, cur_h = FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                        cur_w, cur_h = WINDOW_WIDTH, WINDOW_HEIGHT

        father.update()
        mother.update(father.world_pos)
        daughter.update(mother.world_pos)
        
        screen.fill(COLOR_OUTSIDE)
        cam_iso = (father.world_pos.x - father.world_pos.y, (father.world_pos.x + father.world_pos.y) / 2)
        off_x, off_y = cur_w // 2 - cam_iso[0], cur_h // 2 - cam_iso[1]
        
        # 맵 그리기
        draw_apartment_map(screen, apt_map, (off_x, off_y), cur_w, cur_h)
        
        # 캐릭터 그리기
        daughter.draw(screen, (off_x, off_y))
        mother.draw(screen, (off_x, off_y))
        father.draw(screen, (off_x, off_y))
        
        # UI
        text = font.render("아파트 7층 - 우리집 | WASD: 이동", True, (0, 0, 0))
        text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
        text_bg.fill((255, 255, 255))
        text_bg.set_alpha(200)
        screen.blit(text_bg, (10, 10))
        screen.blit(text, (20, 15))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()