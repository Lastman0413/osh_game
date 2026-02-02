import pygame
import math

# --- 기초 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
FPS = 60
TILE_SIZE = 40

# 색상 (미니의 커스텀 팔레트)
COLOR_BG = (30, 30, 35)       # 심해색 (배경)
COLOR_WALL = (160, 150, 140)   # 벽면
COLOR_WALL_TOP = (180, 170, 160) # 벽 윗면 (두께)
COLOR_FLOOR = (100, 100, 110)  # 바닥 타일
COLOR_GRID = (80, 80, 90)      # 그리드 선

# --- 수학 함수 ---
def to_iso(x, y):
    """월드 좌표를 화면 이소메트릭 좌표로 변환"""
    return (x - y), (x + y) / 2

# --- 방 설정 클래스 ---
class Room:
    def __init__(self):
        # 방의 시작 타일 좌표와 크기
        self.origin_x = 5
        self.origin_y = 5
        self.tw = 10  # 타일 개수 (가로)
        self.th = 10  # 타일 개수 (세로)
        
        self.wall_h = 100  # 벽 높이 (위로 솟음)
        self.wall_d = 12   # 벽 두께

    def get_floor_rect(self):
        """충돌 계산용 바닥 범위 (월드 좌표)"""
        return pygame.Rect(
            self.origin_x * TILE_SIZE, 
            self.origin_y * TILE_SIZE, 
            self.tw * TILE_SIZE, 
            self.th * TILE_SIZE
        )

# --- 캐릭터 클래스 ---
class Character:
    def __init__(self, x, y, color, role="member"):
        self.world_pos = pygame.Vector2(x, y)
        self.speed = 5
        self.color = color
        self.role = role
        self.radius = 15
        self.walk_count = 0
        self.look_dir = pygame.Vector2(0, 1)

    def update(self, target_pos=None, room=None):
        move_vec = pygame.Vector2(0, 0)

        if target_pos is None: # 플레이어 제어
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
        else: # AI 추적
            diff = target_pos - self.world_pos
            if diff.length() > 60:
                move_vec = diff.normalize() * (self.speed * 0.9)
                self.look_dir = pygame.Vector2(move_vec.x - move_vec.y, move_vec.x + move_vec.y).normalize()

        if move_vec.length() > 0:
            self.walk_count += 0.2
            floor_rect = room.get_floor_rect()
            
            # X축 이동 및 벽 충돌
            self.world_pos.x += move_vec.x
            if not floor_rect.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.x -= move_vec.x
            
            # Y축 이동 및 벽 충돌
            self.world_pos.y += move_vec.y
            if not floor_rect.collidepoint(self.world_pos.x, self.world_pos.y):
                self.world_pos.y -= move_vec.y
        else:
            self.walk_count = 0

    def draw(self, surface, cam_off):
        ix, iy = to_iso(self.world_pos.x, self.world_pos.y)
        cx, cy = ix + cam_off[0], iy + cam_off[1]
        
        # 간단한 캐릭터 드로잉 (미니 스타일)
        bob = abs(math.sin(self.walk_count)) * 5
        # 그림자
        pygame.draw.ellipse(surface, (20, 20, 20, 100), (cx-15, cy-7, 30, 15))
        # 몸통
        pygame.draw.circle(surface, self.color, (int(cx), int(cy - 25 - bob)), 15)
        # 머리
        pygame.draw.circle(surface, (255, 220, 200), (int(cx), int(cy - 45 - bob)), 10)

# --- 렌더링 엔진 ---
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

    # 2. 벽 그리기 (북쪽 & 동쪽) - 바닥에서 위로 솟게 설정
    # 북쪽 벽 (Top-Left)
    bx, by = room.origin_x * TILE_SIZE, room.origin_y * TILE_SIZE
    ex, ey = (room.origin_x + room.tw) * TILE_SIZE, room.origin_y * TILE_SIZE
    b_iso = to_iso(bx, by)
    e_iso = to_iso(ex, ey)
    
    # 벽면 (옆면)
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL, wall_pts)
    # 벽 두께 (윗면)
    top_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h - room.wall_d + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h - room.wall_d + cam_off[1])
    ]
    pygame.draw.polygon(screen, COLOR_WALL_TOP, top_pts)

    # 동쪽 벽 (Top-Right)
    bx, by = (room.origin_x + room.tw) * TILE_SIZE, room.origin_y * TILE_SIZE
    ex, ey = (room.origin_x + room.tw) * TILE_SIZE, (room.origin_y + room.th) * TILE_SIZE
    b_iso = to_iso(bx, by)
    e_iso = to_iso(ex, ey)
    
    wall_pts = [
        (b_iso[0] + cam_off[0], b_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] + cam_off[1]),
        (e_iso[0] + cam_off[0], e_iso[1] - room.wall_h + cam_off[1]),
        (b_iso[0] + cam_off[0], b_iso[1] - room.wall_h + cam_off[1])
    ]
    pygame.draw.polygon(screen, (COLOR_WALL[0]-20, COLOR_WALL[1]-20, COLOR_WALL[2]-20), wall_pts)
    
    # 3. 캐릭터 그리기
    for char in characters:
        char.draw(screen, cam_off)

# --- 메인 루프 ---
def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("미니의 정교한 이소메트릭 룸")
    clock = pygame.time.Clock()
    
    room = Room()
    father = Character(400, 400, (70, 130, 180), "father")
    mother = Character(350, 350, (220, 120, 140), "mother")
    
    chars = [mother, father] # 그리기 순서 (뒤에 있는 캐릭터 먼저)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        father.update(room=room)
        mother.update(father.world_pos, room)
        
        # 카메라: 아빠를 중앙에
        ix, iy = to_iso(father.world_pos.x, father.world_pos.y)
        cam_off = (WINDOW_WIDTH//2 - ix, WINDOW_HEIGHT//2 - iy)
        
        render_game(screen, room, chars, cam_off)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()