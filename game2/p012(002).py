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
COLOR_OUTSIDE = (255, 255, 255)
COLOR_ASPHALT = (50, 50, 50)
COLOR_LIGHT_GRID = (70, 70, 70)
COLOR_BORDER_LINE = (255, 0, 0)
COLOR_BACKPACK = (85, 107, 47)
COLOR_LIMB = (255, 203, 164)  # 팔다리도 피부색으로

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class Character:
    def __init__(self, x, y, role="father"):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        self.role = role
        
        # 🔧 5등신 비율: 귀엽고 통통하게
        if role == "father":
            self.limb_len = 20  # 다리 짧게
            self.body_h = 30    # 몸통 짧게
            self.body_w = 22    # 몸통 넓게
            self.head_r = 14    # 머리 크게!
            self.head_color = (255, 203, 164)
            self.body_color = (70, 130, 180)
            self.pants_color = (40, 60, 80)
            self.hair_color = (50, 40, 30)
            self.speed = 7
        elif role == "mother":
            self.limb_len = 18
            self.body_h = 28
            self.body_w = 20
            self.head_r = 13
            self.head_color = (255, 218, 185)
            self.body_color = (220, 120, 140)
            self.pants_color = (60, 50, 70)
            self.hair_color = (80, 50, 30)  # 갈색 머리
            self.ponytail_color = (70, 45, 25)  # 포니테일용
            self.speed = 7
        elif role == "daughter":
            self.limb_len = 14
            self.body_h = 20
            self.body_w = 16
            self.head_r = 11
            self.head_color = (255, 228, 196)
            self.body_color = (255, 220, 100)
            self.pants_color = (100, 150, 200)
            self.hair_color = (40, 30, 20)  # 검은 머리
            self.ribbon_color = (255, 100, 150)  # 양갈래 리본
            self.speed = 7.2

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

        self.world_pos.x = max(0, min(self.world_pos.x, MAP_LIMIT))
        self.world_pos.y = max(0, min(self.world_pos.y, MAP_LIMIT))

    def draw(self, surface, cam_off):
        iso_p = (self.world_pos.x - self.world_pos.y, (self.world_pos.x + self.world_pos.y) / 2)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]
        
        swing = math.sin(self.walk_count) * (self.limb_len / 2.5)  # 스윙 감소
        bobbing = abs(math.sin(self.walk_count)) * 2.5  # 바운싱 감소
        pelvis_y = cy - self.limb_len
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        draw_w = self.body_w - 4 if is_side else self.body_w
        
        # 🎒 배낭 (작고 자연스럽게)
        bag_w, bag_h = draw_w + 2, self.body_h - 18
        bag_rect = (cx - bag_w//2, pelvis_y - self.body_h + 10 + bobbing, bag_w, bag_h)
        if not is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        # 👖 바지 (하의) - 골반부터 무릎까지
        pants_h = self.body_h // 2
        pants_rect = (cx - draw_w//2, pelvis_y - pants_h, draw_w, pants_h)
        pygame.draw.rect(surface, self.pants_color, pants_rect)
        
        # 🦵 다리 (가늘게, 피부색)
        leg_thickness = 2
        pygame.draw.line(surface, COLOR_LIMB, (cx - 4, pelvis_y), (cx - 4 - swing/2, cy + swing/2), leg_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 4, pelvis_y), (cx + 4 + swing/2, cy - swing/2), leg_thickness)
        
        # 👕 상의 (몸통)
        body_top = pelvis_y - pants_h
        body_rect = (cx - draw_w//2, body_top - (self.body_h - pants_h), draw_w, self.body_h - pants_h)
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (200, 200, 200), body_rect, 1)  # 테두리
        
        if is_back: 
            pygame.draw.rect(surface, COLOR_BACKPACK, bag_rect, border_radius=2)
        
        # 💪 팔 (가늘게, 피부색)
        shoulder_y = body_top - (self.body_h - pants_h) + 3
        arm_thickness = 2
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y), 
                        (cx - draw_w//2 - 8, shoulder_y + 18 - swing), arm_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y), 
                        (cx + draw_w//2 + 8, shoulder_y + 18 + swing), arm_thickness)
        
        # 👤 머리
        head_y = shoulder_y - 8
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)
        
        # 💇 머리카락 (역할별 스타일)
        if self.role == "father":
            # 아빠: 짧은 머리
            if not is_back:
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
        
        elif self.role == "mother":
            # 엄마: 포니테일 (시선 방향에 따라 위치 조정)
            if not is_back:
                # 앞머리
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r + 2)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
                # 포니테일 위치 계산 (시선 반대편에)
                ponytail_offset_x = -self.look_dir.x * 10  # 좌우 반대
                ponytail_offset_y = -self.look_dir.y * 5   # 상하 반대
                ponytail_x = cx + ponytail_offset_x - 5
                ponytail_y = head_y + 4 + ponytail_offset_y
                pygame.draw.ellipse(surface, self.ponytail_color, 
                                   (ponytail_x, ponytail_y, 10, 16))
            else:
                # 뒤: 포니테일 잘 보임
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
                ponytail_x = cx - 5
                ponytail_y = head_y + 6
                pygame.draw.ellipse(surface, self.ponytail_color, 
                                   (ponytail_x, ponytail_y, 10, 18))
        
        elif self.role == "daughter":
            # 딸: 양갈래 머리 (시선 방향에 따라 위치 조정)
            if not is_back:
                # 앞머리
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
                # 양갈래 위치 계산 (머리 양옆, 시선에 따라 깊이감)
                pigtail_base_y = head_y + 2
                # 왼쪽 양갈래 (시선 왼쪽이면 앞으로, 오른쪽이면 뒤로)
                left_depth = -self.look_dir.x * 3  # 시선 방향 반대로 깊이
                left_pigtail_x = cx - self.head_r - 3 + left_depth
                left_pigtail_y = pigtail_base_y - self.look_dir.y * 2
                pygame.draw.circle(surface, self.hair_color, (int(left_pigtail_x), int(left_pigtail_y)), 5)
                pygame.draw.circle(surface, self.ribbon_color, (int(left_pigtail_x), int(left_pigtail_y - 3)), 3)
                # 오른쪽 양갈래
                right_depth = self.look_dir.x * 3
                right_pigtail_x = cx + self.head_r - 3 + right_depth
                right_pigtail_y = pigtail_base_y - self.look_dir.y * 2
                pygame.draw.circle(surface, self.hair_color, (int(right_pigtail_x), int(right_pigtail_y)), 5)
                pygame.draw.circle(surface, self.ribbon_color, (int(right_pigtail_x), int(right_pigtail_y - 3)), 3)
            else:
                # 뒤: 양갈래 뒤통수에서
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)
                left_pigtail_x = cx - self.head_r - 2
                right_pigtail_x = cx + self.head_r + 2
                pigtail_y = head_y + 4
                pygame.draw.circle(surface, self.hair_color, (int(left_pigtail_x), int(pigtail_y)), 4)
                pygame.draw.circle(surface, self.hair_color, (int(right_pigtail_x), int(pigtail_y)), 4)
        
        # 얼굴 테두리
        pygame.draw.circle(surface, (220, 220, 220), (int(cx), int(head_y)), self.head_r, 1)
        
        # 👀 눈 (앞을 볼 때만)
        if not is_back:
            eye_x, eye_y = cx + self.look_dir.x * 3, head_y + self.look_dir.y * 1.5
            eye_spacing = 4
            # 흰자
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x - eye_spacing), int(eye_y)), 3)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x + eye_spacing), int(eye_y)), 3)
            # 검은자
            pygame.draw.circle(surface, (50, 50, 50), (int(eye_x - eye_spacing), int(eye_y)), 2)
            pygame.draw.circle(surface, (50, 50, 50), (int(eye_x + eye_spacing), int(eye_y)), 2)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("개선된 캐릭터 테스트")
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
                    is_border = (x == 0 or y == 0 or x + TILE_SIZE >= MAP_LIMIT or y + TILE_SIZE >= MAP_LIMIT)
                    pygame.draw.polygon(screen, COLOR_BORDER_LINE if is_border else COLOR_LIGHT_GRID, pts, 1)

        daughter.draw(screen, (off_x, off_y))
        mother.draw(screen, (off_x, off_y))
        father.draw(screen, (off_x, off_y))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()