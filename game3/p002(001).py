import pygame
import math

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
info = pygame.display.Info()
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h

FPS = 60
TILE_SIZE = 40
MAP_WIDTH = 20
MAP_HEIGHT = 20
MAP_LIMIT_X = TILE_SIZE * MAP_WIDTH
MAP_LIMIT_Y = TILE_SIZE * MAP_HEIGHT

# 색상 정의
COLOR_WALL = (180, 160, 140)
COLOR_FLOOR = (220, 210, 190)
COLOR_OUTSIDE = (50, 50, 50)  # 벽 외부 (어두운 회색)
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 203, 164)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

# 벽 정의 (월드 좌표 기준)
class Room:
    def __init__(self):
        # 거실 벽 좌표 (x, y, width, height) - 타일 단위
        self.walls = [
            # 외벽 4개
            {"x": 5, "y": 5, "w": 10, "h": 0, "type": "horizontal"},  # 북쪽
            {"x": 15, "y": 5, "w": 0, "h": 8, "type": "vertical"},   # 동쪽
            {"x": 5, "y": 13, "w": 10, "h": 0, "type": "horizontal"},  # 남쪽
            {"x": 5, "y": 5, "w": 0, "h": 8, "type": "vertical"},    # 서쪽
        ]
        
        # 방 바닥 영역
        self.floor_area = {
            "x": 5,
            "y": 5,
            "w": 10,
            "h": 8
        }

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
        old_pos = self.world_pos.copy()  # 이전 위치 저장
        
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

        # 벽 충돌 체크
        if room:
            floor = room.floor_area
            min_x = floor["x"] * TILE_SIZE + 20  # 약간 여유
            max_x = (floor["x"] + floor["w"]) * TILE_SIZE - 20
            min_y = floor["y"] * TILE_SIZE + 20
            max_y = (floor["y"] + floor["h"]) * TILE_SIZE - 20
            
            # 벽에 부딪히면 이전 위치로 되돌림
            if self.world_pos.x < min_x or self.world_pos.x > max_x or \
               self.world_pos.y < min_y or self.world_pos.y > max_y:
                self.world_pos = old_pos
        
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

def draw_room(surface, room, cam_off, cur_w, cur_h):
    """거실 맵 렌더링 - 벽 중심"""
    
    # 1. 먼저 전체를 어두운 배경으로
    surface.fill(COLOR_OUTSIDE)
    
    # 2. 벽 먼저 그리기 (아래쪽에)
    # 아빠 캐릭터 총 높이: limb_len(20) + body_h(30) + head_r*2(28) = 약 78
    # 벽 높이: 캐릭터의 1.2~1.3배 정도
    wall_height = 90  # 캐릭터보다 약간 큼
    wall_depth = 15   # 벽 두께
    
    for wall in room.walls:
        wx = wall["x"] * TILE_SIZE
        wy = wall["y"] * TILE_SIZE
        
        if wall["type"] == "horizontal":
            ww = wall["w"] * TILE_SIZE
            start_iso_x = wx - wy
            start_iso_y = (wx + wy) / 2
            end_iso_x = (wx + ww) - wy
            end_iso_y = ((wx + ww) + wy) / 2
            
            # 앞면 (세로 벽면)
            front_pts = [
                (start_iso_x + cam_off[0], start_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y + wall_height + cam_off[1]),
                (start_iso_x + cam_off[0], start_iso_y + wall_height + cam_off[1])
            ]
            pygame.draw.polygon(surface, COLOR_WALL, front_pts)
            pygame.draw.polygon(surface, (150, 140, 120), front_pts, 2)
            
            # 윗면 (뒷벽 상단 - 벽 두께)
            top_pts = [
                (start_iso_x + cam_off[0], start_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y - wall_depth + cam_off[1]),
                (start_iso_x + cam_off[0], start_iso_y - wall_depth + cam_off[1])
            ]
            pygame.draw.polygon(surface, (160, 150, 130), top_pts)
            pygame.draw.polygon(surface, (140, 130, 110), top_pts, 2)
            
        elif wall["type"] == "vertical":
            wh = wall["h"] * TILE_SIZE
            start_iso_x = wx - wy
            start_iso_y = (wx + wy) / 2
            end_iso_x = wx - (wy + wh)
            end_iso_y = (wx + (wy + wh)) / 2
            
            # 앞면 (세로 벽면)
            front_pts = [
                (start_iso_x + cam_off[0], start_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y + wall_height + cam_off[1]),
                (start_iso_x + cam_off[0], start_iso_y + wall_height + cam_off[1])
            ]
            pygame.draw.polygon(surface, COLOR_WALL, front_pts)
            pygame.draw.polygon(surface, (150, 140, 120), front_pts, 2)
            
            # 윗면 (뒷벽 상단 - 벽 두께)
            top_pts = [
                (start_iso_x + cam_off[0], start_iso_y + cam_off[1]),
                (end_iso_x + cam_off[0], end_iso_y + cam_off[1]),
                (end_iso_x - wall_depth + cam_off[0], end_iso_y + cam_off[1]),
                (start_iso_x - wall_depth + cam_off[0], start_iso_y + cam_off[1])
            ]
            pygame.draw.polygon(surface, (160, 150, 130), top_pts)
            pygame.draw.polygon(surface, (140, 130, 110), top_pts, 2)
    
    # 3. 바닥 그리기 (벽 위에)
    floor = room.floor_area
    for tx in range(floor["w"]):
        for ty in range(floor["h"]):
            x = (floor["x"] + tx) * TILE_SIZE
            y = (floor["y"] + ty) * TILE_SIZE
            
            iso_x = x - y
            iso_y = (x + y) / 2
            
            pts = [
                (iso_x + cam_off[0], iso_y + cam_off[1]),
                (iso_x + TILE_SIZE + cam_off[0], iso_y + TILE_SIZE/2 + cam_off[1]),
                (iso_x + cam_off[0], iso_y + TILE_SIZE + cam_off[1]),
                (iso_x - TILE_SIZE + cam_off[0], iso_y + TILE_SIZE/2 + cam_off[1])
            ]
            
            pygame.draw.polygon(surface, COLOR_FLOOR, pts)
            pygame.draw.polygon(surface, (200, 200, 200), pts, 1)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("벽 구현 테스트 - 거실")
    clock = pygame.time.Clock()
    is_fullscreen = False
    cur_w, cur_h = WINDOW_WIDTH, WINDOW_HEIGHT
    
    room = Room()
    
    # 캐릭터 시작 위치 (거실 중앙)
    father = Character(400, 360, "father")
    mother = Character(360, 320, "mother")
    daughter = Character(320, 280, "daughter")
    
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

        father.update(room=room)
        mother.update(father.world_pos, room)
        daughter.update(mother.world_pos, room)
        
        cam_iso = (father.world_pos.x - father.world_pos.y, (father.world_pos.x + father.world_pos.y) / 2)
        off_x, off_y = cur_w // 2 - cam_iso[0], cur_h // 2 - cam_iso[1]
        
        # 맵 그리기
        draw_room(screen, room, (off_x, off_y), cur_w, cur_h)
        
        # 캐릭터 그리기
        daughter.draw(screen, (off_x, off_y))
        mother.draw(screen, (off_x, off_y))
        father.draw(screen, (off_x, off_y))
        
        # UI
        text = font.render("거실 (벽 테스트) | WASD: 이동", True, (255, 255, 255))
        text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
        text_bg.fill((0, 0, 0))
        text_bg.set_alpha(150)
        screen.blit(text_bg, (10, 10))
        screen.blit(text, (20, 15))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()