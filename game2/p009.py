import pygame
import math

# --- 설정 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 60
MAP_TILES = 40 
MAP_LIMIT = TILE_SIZE * MAP_TILES

# 색상 테마
COLOR_OUTSIDE = (255, 255, 255)
COLOR_ASPHALT = (50, 50, 50)
COLOR_LIGHT_GRID = (200, 200, 200)
COLOR_BACKPACK = (85, 107, 47) # 카키색 가방
COLOR_LIMB = (255, 255, 255)

class Character:
    def __init__(self, x, y, role="father"):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        self.role = role
        
        # 역할별 신체 규격 및 색상 정의
        if role == "father":
            self.limb_len, self.body_h, self.body_w, self.head_r = 22, 35, 24, 13
            self.head_color, self.body_color = (255, 203, 164), (135, 206, 235) # 아빠 (기존)
            self.speed = 7
        elif role == "mother":
            self.limb_len, self.body_h, self.body_w, self.head_r = 20, 32, 20, 12
            self.head_color, self.body_color = (255, 218, 185), (255, 182, 193) # 엄마 (분홍 계열)
            self.speed = 7
        elif role == "daughter":
            self.limb_len, self.body_h, self.body_w, self.head_r = 14, 22, 16, 9
            self.head_color, self.body_color = (255, 228, 196), (255, 255, 150) # 딸 (노랑 계열)
            self.speed = 7.2 # 어린애라 조금 더 발랄하게

    def update(self, target_pos=None):
        if target_pos is None: # 직접 조작 (아빠)
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
        else: # 따라가기 AI (엄마, 딸)
            dist_vec = target_pos - self.world_pos
            if dist_vec.length() > 50: # 일정 거리 유지
                move_dir = dist_vec.normalize()
                # look_dir을 이동 방향에 맞게 화면 좌표계로 역산
                self.look_dir = pygame.Vector2(move_dir.x - move_dir.y, move_dir.x + move_dir.y).normalize()
                self.world_pos += move_dir * self.speed
                self.walk_count += 0.2
            else: self.walk_count = 0

    def draw(self, surface, cam_off):
        # 월드 좌표를 스크린 좌표로 변환
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
        
        # 다리
        pygame.draw.line(surface, COLOR_LIMB, (cx - 5, pelvis_y), (cx - 5 - swing/2, cy + swing/2), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 5, pelvis_y), (cx + 5 + swing/2, cy - swing/2), 3)
        
        # 몸통
        body_rect = (cx - draw_w//2, pelvis_y - self.body_h, draw_w, self.body_h)
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 1)

        if is_back: pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect)

        # 팔/머리
        shoulder_y = pelvis_y - self.body_h + 5
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y), (cx - draw_w//2 - 6, shoulder_y + 15 - swing), 3)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y), (cx + draw_w//2 + 6, shoulder_y + 15 + swing), 3)

        head_y = shoulder_y - 10
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)
        pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(head_y)), self.head_r, 1)
        
        if not is_back: # 눈
            eye_x, eye_y = cx + self.look_dir.x * 4, head_y + self.look_dir.y * 2
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x - 3), int(eye_y)), 2)
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x + 3), int(eye_y)), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # 가족 생성
    father = Character(MAP_LIMIT/2, MAP_LIMIT/2, "father")
    mother = Character(MAP_LIMIT/2 - 40, MAP_LIMIT/2 - 40, "mother")
    daughter = Character(MAP_LIMIT/2 - 80, MAP_LIMIT/2 - 80, "daughter")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        # 업데이트 (아빠를 중심으로 대열 이동)
        father.update()
        mother.update(father.world_pos)
        daughter.update(mother.world_pos) # 딸은 엄마를 따라감
        
        screen.fill(COLOR_OUTSIDE)
        
        # 카메라 오프셋 (아빠 중심)
        cam_iso = (father.world_pos.x - father.world_pos.y, (father.world_pos.x + father.world_pos.y) / 2)
        off_x, off_y = SCREEN_WIDTH // 2 - cam_iso[0], SCREEN_HEIGHT // 2 - cam_iso[1]
        
        # 맵 렌더링 최적화
        for x in range(0, MAP_LIMIT, TILE_SIZE):
            for y in range(0, MAP_LIMIT, TILE_SIZE):
                p = (x - y, (x + y) / 2)
                if -150 < p[0] + off_x < SCREEN_WIDTH + 150 and -150 < p[1] + off_y < SCREEN_HEIGHT + 150:
                    pts = [(p[0]+off_x, p[1]+off_y) for p in [(x-y,(x+y)/2), (x+TILE_SIZE-y,(x+TILE_SIZE+y)/2), (x+TILE_SIZE-(y+TILE_SIZE),(x+TILE_SIZE+y+TILE_SIZE)/2), (x-(y+TILE_SIZE),(x+y+TILE_SIZE)/2)]]
                    pygame.draw.polygon(screen, COLOR_ASPHALT, pts)
                    pygame.draw.polygon(screen, COLOR_LIGHT_GRID, pts, 1)

        # 가족 그리기
        daughter.draw(screen, (off_x, off_y))
        mother.draw(screen, (off_x, off_y))
        father.draw(screen, (off_x, off_y))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()