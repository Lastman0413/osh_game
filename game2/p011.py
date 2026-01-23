
import pygame
import math

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
info = pygame.display.Info()
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h

FPS = 60
TILE_SIZE = 60
MAP_TILES = 40 
MAP_LIMIT = TILE_SIZE * MAP_TILES

# 색상 정의
COLOR_OUTSIDE = (255, 255, 255)  # 맵 외부 (흰색)
COLOR_ASPHALT = (50, 50, 50)     # 아스팔트 (전면)
COLOR_LIGHT_GRID = (70, 70, 70)  # 격자 (아스팔트와 대비되는 짙은 회색)
COLOR_BORDER_LINE = (255, 0, 0)  # 맵 끝 경계선 (빨간색)
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 255, 255)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Character:
    def __init__(self, x, y, role="father"):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        self.role = role
        
        # 신체 규격 보존
        if role == "father":
            self.limb_len, self.body_h, self.body_w, self.head_r = 22, 35, 24, 13
            self.head_color, self.body_color = (255, 203, 164), (135, 206, 235)
            self.speed = 7
        elif role == "mother":
            self.limb_len, self.body_h, self.body_w, self.head_r = 20, 32, 20, 12
            self.head_color, self.body_color = (255, 218, 185), (255, 182, 193)
            self.speed = 7
        elif role == "daughter":
            self.limb_len, self.body_h, self.body_w, self.head_r = 14, 22, 16, 9
            self.head_color, self.body_color = (255, 228, 196), (255, 255, 150)
            self.speed = 7.2

    def update(self, target_pos=None):
        if target_pos is None: # 아빠 조작
            keys = pygame.key.get_pressed()
            screen_move = pygame.Vector2(0, 0)
            if keys[pygame.K_w]: screen_move.y -= 1
            if keys[pygame.K_s]: screen_move.y += 1
            if keys[pygame.K_a]: screen_move.x -= 1
            if keys[pygame.K_d]: screen_move.x += 1
            
            if screen_move.length() > 0:
                screen_move = screen_move.normalize()
                # 90도 이동 보정 로직 보존
                world_move = pygame.Vector2(screen_move.x + screen_move.y, -screen_move.x + screen_move.y).normalize()
                self.look_dir = screen_move
                self.world_pos += world_move * self.speed
                self.walk_count += 0.2
            else: self.walk_count = 0
        else: # 따라가기 (엄마, 딸)
            dist_vec = target_pos - self.world_pos
            if dist_vec.length() > 65:
                move_dir = dist_vec.normalize()
                self.look_dir = pygame.Vector2(move_dir.x - move_dir.y, move_dir.x + move_dir.y).normalize()
                self.world_pos += move_dir * self.speed
                self.walk_count += 0.2
            else: self.walk_count = 0

        # [명령 이행] 강력한 맵 경계 고정 (0 ~ 2400 사이로 물리적 제한)
        self.world_pos.x = max(0, min(self.world_pos.x, MAP_LIMIT))
        self.world_pos.y = max(0, min(self.world_pos.y, MAP_LIMIT))

    def draw(self, surface, cam_off):
        iso_p = (self.world_pos.x - self.world_pos.y, (self.world_pos.x + self.world_pos.y) / 2)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
        
        swing = math.sin(self.walk_count) * (self.limb_len / 2)
        bobbing = abs(math.sin(self.walk_count)) * 3
        pelvis_y = cy - self.limb_len
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        draw_w = self.body_w - 6 if is_side else self.body_w
        
        bag_rect = (cx - draw_w//2 - 2, pelvis_y - self.body_h + 8 + bobbing, draw_w + 4, self.body_h - 10)
        if not is_back: pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect)
        pygame.draw.line(surface, COLOR_LIMB, (cx - 5, pelvis_y), (cx - 5 - swing/2, cy + swing/2), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 5, pelvis_y), (cx + 5 + swing/2, cy - swing/2), 3)
        body_rect = (cx - draw_w//2, pelvis_y - self.body_h, draw_w, self.body_h)
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 1)
        if is_back: pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect)
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y), (cx - draw_w//2 - 6, shoulder_y + 15 - swing), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y), (cx + draw_w//2 + 6, shoulder_y + 15 + swing), 3)
        head_y = shoulder_y - 10
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)
        pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(head_y)), self.head_r, 1)
        if not is_back:
            eye_x, eye_y = cx + self.look_dir.x * 4, head_y + self.look_dir.y * 2
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x - 3), int(eye_y)), 2)
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x + 3), int(eye_y)), 2)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    is_fullscreen = False
    cur_w, cur_h = WINDOW_WIDTH, WINDOW_HEIGHT
    
    father = Character(MAP_LIMIT/2, MAP_LIMIT/2, "father")
    mother = Character(MAP_LIMIT/2 - 40, MAP_LIMIT/2 - 40, "mother")
    daughter = Character(MAP_LIMIT/2 - 80, MAP_LIMIT/2 - 80, "daughter")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
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
        
        # 맵 렌더링 (아스팔트 전면 도색 및 경계선 강조)
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                p = (x - y, (x + y) / 2)
                if -150 < p[0] + off_x < cur_w + 150 and -150 < p[1] + off_y < cur_h + 150:
                    pts = [(p[0]+off_x, p[1]+off_y) for p in [
                        (x-y, (x+y)/2), 
                        (x+TILE_SIZE-y, (x+TILE_SIZE+y)/2), 
                        (x+TILE_SIZE-(y+TILE_SIZE), (x+TILE_SIZE+y+TILE_SIZE)/2), 
                        (x-(y+TILE_SIZE), (x+y+TILE_SIZE)/2)
                    ]]
                    pygame.draw.polygon(screen, COLOR_ASPHALT, pts)
                    # 경계 타일 판정
                    is_border = (x == 0 or y == 0 or x + TILE_SIZE >= MAP_LIMIT or y + TILE_SIZE >= MAP_LIMIT)
                    pygame.draw.polygon(screen, COLOR_BORDER_LINE if is_border else COLOR_LIGHT_GRID, pts, 1)

        daughter.draw(screen, (off_x, off_y))
        mother.draw(screen, (off_x, off_y))
        father.draw(screen, (off_x, off_y))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()