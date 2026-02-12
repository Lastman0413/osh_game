import pygame
import math
import random

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
info = pygame.display.Info()
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h

FPS = 60
TILE_SIZE = 40

COLOR_WALL = (100, 90, 80)
COLOR_FLOOR = (200, 190, 180)
COLOR_OUTSIDE = (30, 30, 35)
COLOR_BACKPACK = (85, 70, 50)
COLOR_LIMB = (255, 220, 180)

COLOR_TEXT = (255, 250, 240)
COLOR_TEXT_SHADOW = (50, 40, 40)
COLOR_DIALOG_BG = (0, 0, 0, 200)
COLOR_HP_BAR = (200, 50, 50)
COLOR_HP_BG = (80, 30, 30)
COLOR_TIMER = (255, 200, 100)

def iso_projection(x, y):
    return (x - y), (x + y) / 2

class FamilyMember:
    def __init__(self, x, y, role, name):
        self.world_pos = pygame.Vector2(x, y)
        self.look_dir = pygame.Vector2(0, 1)
        self.walk_count = 0
        self.role = role
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.state = "normal"
        self.is_controlled = False

        if role == "father":
            self.limb_len = 20
            self.body_h = 30
            self.body_w = 22
            self.head_r = 14
            self.head_color = (255, 220, 180)
            self.body_color = (70, 100, 140)
            self.pants_color = (50, 60, 80)
            self.hair_color = (60, 50, 40)
            self.speed = 4
            self.ability_name = "보호"
            self.ability_desc = "가족을 위해 무거운 것을 옮기고 위험을 막음"

        elif role == "mother":
            self.limb_len = 18
            self.body_h = 28
            self.body_w = 20
            self.head_r = 13
            self.head_color = (255, 230, 200)
            self.body_color = (200, 120, 130)
            self.pants_color = (70, 60, 80)
            self.hair_color = (90, 60, 40)
            self.ponytail_color = (80, 55, 35)
            self.speed = 4
            self.ability_name = "치료"
            self.ability_desc = "상처받은 가족을 돌보고 체력을 회복시킴"

        elif role == "daughter":
            self.limb_len = 14
            self.body_h = 20
            self.body_w = 16
            self.head_r = 11
            self.head_color = (255, 240, 220)
            self.body_color = (240, 200, 100)
            self.pants_color = (120, 150, 200)
            self.hair_color = (50, 40, 30)
            self.ribbon_color = (255, 120, 160)
            self.speed = 6
            self.ability_name = "정찰"
            self.ability_desc = "빠르게 이동하여 앞을 확인하고 길을 찾음"

        elif role == "dog":
            self.limb_len = 8
            self.body_h = 12
            self.body_w = 14
            self.head_r = 8
            self.head_color = (220, 180, 140)
            self.body_color = (180, 140, 100)
            self.pants_color = None
            self.hair_color = (160, 120, 80)
            self.speed = 7
            self.ability_name = "발견"
            self.ability_desc = "숨겨진 물건을 찾고 위험을 미리 알려줌"

    def update(self, target_pos=None, room=None):
        if not pygame.display.get_init():
            return
        
        old_pos = self.world_pos.copy()

        if target_pos is None:
            if not self.is_controlled:
                return

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
                self.walk_count += 0.3
            else:
                self.walk_count = 0
        else:
            dist_vec = target_pos - self.world_pos
            if dist_vec.length() > 50:
                move_dir = dist_vec.normalize()
                self.look_dir = pygame.Vector2(move_dir.x - move_dir.y, move_dir.x + move_dir.y).normalize()
                self.world_pos += move_dir * self.speed * 0.9
                self.walk_count += 0.3
            else:
                self.walk_count = 0

        if room:
            floor = room.floor_area
            min_x = floor["x"] * TILE_SIZE
            max_x = (floor["x"] + floor["w"]) * TILE_SIZE
            min_y = floor["y"] * TILE_SIZE
            max_y = (floor["y"] + floor["h"]) * TILE_SIZE

            margin = self.body_w
            if not (min_x + margin <= self.world_pos.x <= max_x - margin and \
                    min_y + margin <= self.world_pos.y <= max_y - margin):
                self.world_pos = old_pos

    def draw(self, surface, cam_off):
        iso_p = (self.world_pos.x - self.world_pos.y, (self.world_pos.x + self.world_pos.y) / 2)
        cx, cy = iso_p[0] + cam_off[0], iso_p[1] + cam_off[1]

        swing = math.sin(self.walk_count) * (self.limb_len / 3)
        bobbing = abs(math.sin(self.walk_count)) * 2

        if self.role == "dog":
            self.draw_dog(surface, cx, cy, swing, bobbing)
        else:
            self.draw_human(surface, cx, cy, swing, bobbing)

    def draw_human(self, surface, cx, cy, swing, bobbing):
        pelvis_y = cy - self.limb_len
        is_back = self.look_dir.y < -0.1
        is_side = abs(self.look_dir.x) > 0.5
        draw_w = self.body_w - 4 if is_side else self.body_w

        if self.pants_color:
            pants_h = self.body_h // 2
            pants_rect = (cx - draw_w//2, pelvis_y - pants_h, draw_w, pants_h)
            pygame.draw.rect(surface, self.pants_color, pants_rect)

        leg_thickness = 2 if self.role != "daughter" else 1
        pygame.draw.line(surface, COLOR_LIMB, (cx - 3, pelvis_y), (cx - 3 - swing/2, cy + swing/2), leg_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + 3, pelvis_y), (cx + 3 + swing/2, cy - swing/2), leg_thickness)

        body_top = pelvis_y - (self.body_h // 2 if self.pants_color else self.body_h)
        body_rect = (cx - draw_w//2, body_top - (self.body_h - (self.body_h // 2 if self.pants_color else 0)), draw_w, self.body_h - (self.body_h // 2 if self.pants_color else 0))
        pygame.draw.rect(surface, self.body_color, body_rect)
        pygame.draw.rect(surface, (200, 200, 200), body_rect, 1)

        shoulder_y = body_top - (self.body_h - (self.body_h // 2 if self.pants_color else 0)) + 3
        arm_thickness = 2 if self.role != "daughter" else 1
        pygame.draw.line(surface, COLOR_LIMB, (cx - draw_w//2, shoulder_y),
                        (cx - draw_w//2 - 6, shoulder_y + 12 - swing), arm_thickness)
        pygame.draw.line(surface, COLOR_LIMB, (cx + draw_w//2, shoulder_y),
                        (cx + draw_w//2 + 6, shoulder_y + 12 + swing), arm_thickness)

        head_y = shoulder_y - 6
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
                    ponytail_offset_x = -self.look_dir.x * 8
                    ponytail_offset_y = -self.look_dir.y * 4
                    ponytail_x = cx + ponytail_offset_x - 4
                    ponytail_y = head_y + 3 + ponytail_offset_y
                    pygame.draw.ellipse(surface, self.ponytail_color, (ponytail_x, ponytail_y, 8, 14))
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)

        elif self.role == "daughter":
            if not is_back:
                hair_rect = (cx - self.head_r + 2, head_y - self.head_r, self.head_r * 2 - 4, self.head_r)
                pygame.draw.ellipse(surface, self.hair_color, hair_rect)
            else:
                pygame.draw.circle(surface, self.hair_color, (int(cx), int(head_y - 2)), self.head_r - 1)

        pygame.draw.circle(surface, (220, 220, 220), (int(cx), int(head_y)), self.head_r, 1)

        if not is_back:
            eye_x, eye_y = cx + self.look_dir.x * 2, head_y + self.look_dir.y * 1
            eye_spacing = 3 if self.role != "daughter" else 2
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x - eye_spacing), int(eye_y)), 3 if self.role != "daughter" else 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x + eye_spacing), int(eye_y)), 3 if self.role != "daughter" else 2)
            pygame.draw.circle(surface, (40, 40, 40), (int(eye_x - eye_spacing), int(eye_y)), 2 if self.role != "daughter" else 1)
            pygame.draw.circle(surface, (40, 40, 40), (int(eye_x + eye_spacing), int(eye_y)), 2 if self.role != "daughter" else 1)

        if self.is_controlled:
            pygame.draw.circle(surface, (255, 255, 0), (int(cx), int(head_y - self.head_r - 10)), 4)

    def draw_dog(self, surface, cx, cy, swing, bobbing):
        body_y = cy - self.limb_len
        body_w = self.body_w
        body_h = self.body_h

        pygame.draw.ellipse(surface, self.body_color, (cx - body_w//2, body_y - body_h, body_w, body_h))

        leg_y = body_y
        pygame.draw.line(surface, self.hair_color, (cx - 4, leg_y), (cx - 4 - swing/2, leg_y + 6), 2)
        pygame.draw.line(surface, self.hair_color, (cx + 4, leg_y), (cx + 4 + swing/2, leg_y + 6), 2)

        head_y = body_y - body_h + 2
        pygame.draw.circle(surface, self.head_color, (int(cx), int(head_y)), self.head_r)

        if not self.look_dir.y < -0.1:
            ear_x = cx - self.look_dir.x * 4
            ear_y = head_y - 4
            pygame.draw.ellipse(surface, self.hair_color, (ear_x - 3, ear_y - 3, 6, 8))

        nose_x = cx + self.look_dir.x * 4
        nose_y = head_y + 2
        pygame.draw.circle(surface, (40, 30, 20), (int(nose_x), int(nose_y)), 3)

        if self.is_controlled:
            pygame.draw.circle(surface, (255, 255, 0), (int(cx), int(head_y - self.head_r - 8)), 4)

class Room:
    def __init__(self, name, x, y, w, h, is_transition=False, next_room=None):
        self.name = name
        self.floor_area = {"x": x, "y": y, "w": w, "h": h}
        self.is_transition = is_transition
        self.next_room = next_room
        self.walls = self.create_walls(x, y, w, h)
        self.events = []
        self.puzzles = []
        self.is_completed = False
        self.rendered_surface = None

    def create_walls(self, x, y, w, h):
        walls = [
            {"x": x, "y": y, "w": w, "h": 0, "type": "horizontal"},
            {"x": x + w, "y": y, "w": 0, "h": h, "type": "vertical"},
            {"x": x, "y": y + h, "w": w, "h": 0, "type": "horizontal"},
            {"x": x, "y": y, "w": 0, "h": h, "type": "vertical"},
        ]
        return walls

    def pre_render(self, tile_size):
        floor = self.floor_area
        surf_w = (floor["w"] + floor["h"]) * tile_size + 100
        surf_h = (floor["w"] + floor["h"]) * tile_size // 2 + 100
        self.rendered_surface = pygame.Surface((int(surf_w), int(surf_h)), pygame.SRCALPHA)

        for tx in range(floor["w"]):
            for ty in range(floor["h"]):
                x = (floor["x"] + tx) * tile_size
                y = (floor["y"] + ty) * tile_size
                iso_x = x - y
                iso_y = (x + y) / 2
                pts = [
                    (iso_x + 50, iso_y + 50),
                    (iso_x + tile_size + 50, iso_y + tile_size/2 + 50),
                    (iso_x + 50, iso_y + tile_size + 50),
                    (iso_x - tile_size + 50, iso_y + tile_size/2 + 50)
                ]
                pygame.draw.polygon(self.rendered_surface, (200, 190, 180), pts)
                pygame.draw.polygon(self.rendered_surface, (180, 180, 180), pts, 1)

        for wall in self.walls:
            wx = wall["x"] * tile_size
            wy = wall["y"] * tile_size
            if wall["type"] == "horizontal":
                ww = wall["w"] * tile_size
                start_x = wx - wy
                start_y = (wx + wy) / 2
                end_x = (wx + ww) - wy
                end_y = (wx + ww + wy) / 2
                wall_height = 40
                wall_pts = [
                    (start_x + 50, start_y + 50),
                    (end_x + 50, end_y + 50),
                    (end_x + 50, end_y + wall_height + 50),
                    (start_x + 50, start_y + wall_height + 50)
                ]
                pygame.draw.polygon(self.rendered_surface, (100, 90, 80), wall_pts)
                pygame.draw.polygon(self.rendered_surface, (80, 70, 60), wall_pts, 2)
            elif wall["type"] == "vertical":
                wh = wall["h"] * tile_size
                start_x = wx - wy
                start_y = (wx + wy) / 2
                end_x = wx - (wy + wh)
                end_y = (wx + wy + wh) / 2
                wall_height = 40
                wall_pts = [
                    (start_x + 50, start_y + 50),
                    (end_x + 50, end_y + 50),
                    (end_x + 50, end_y + wall_height + 50),
                    (start_x + 50, start_y + wall_height + 50)
                ]
                pygame.draw.polygon(self.rendered_surface, (100, 90, 80), wall_pts)
                pygame.draw.polygon(self.rendered_surface, (80, 70, 60), wall_pts, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("그리운 집으로 - 가족 여정")
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False
        self.cur_w, self.cur_h = WINDOW_WIDTH, WINDOW_HEIGHT

        # ✅ 한글 폰트
        try:
            self.font = pygame.font.SysFont('malgungothic', 28)
            self.font_small = pygame.font.SysFont('malgungothic', 22)
            self.font_title = pygame.font.SysFont('malgungothic', 48)
        except:
            try:
                self.font = pygame.font.SysFont('nanumgothic', 28)
                self.font_small = pygame.font.SysFont('nanumgothic', 22)
                self.font_title = pygame.font.SysFont('nanumgothic', 48)
            except:
                self.font = pygame.font.Font(None, 28)
                self.font_small = pygame.font.Font(None, 22)
                self.font_title = pygame.font.Font(None, 48)

        self.state = "intro"
        self.current_room_index = 0
        self.rooms = self.create_rooms()
        self.family = self.create_family()
        self.current_member = 0
        self.story_progress = 0
        self.game_time = 0
        self.max_time = 5400
        self.is_game_over = False
        self.ending_type = None

        self.dialogs = self.create_dialogs()
        self.current_dialog = None
        self.dialog_index = 0
        self.dialog_timer = 0

        self.secret_items_found = 0
        self.required_items = 3
        
        self.cam_off = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    def create_rooms(self):
        return [
            Room("현관", 50, 50, 60, 50, next_room=1),
            Room("복도", 110, 50, 40, 50, next_room=2),
            Room("로비", 150, 50, 80, 60, next_room=3),
            Room("고미술관", 50, 100, 80, 60, next_room=4),
            Room("역사관", 130, 110, 80, 60, next_room=5),
            Room("자연관", 50, 160, 80, 60, next_room=6),
            Room("출구", 130, 170, 60, 50, is_transition=True),
        ]

    def create_family(self):
        return [
            FamilyMember(3200, 3400, "father", "아빠"),
            FamilyMember(2800, 3000, "mother", "엄마"),
            FamilyMember(2400, 2600, "daughter", "딸"),
            FamilyMember(2600, 2800, "dog", "강아지"),
        ]

    def create_dialogs(self):
        return {
            0: [
                ("엄마", "오늘 할머니 댁에 가야지. 오래 만났으니까"),
                ("아빠", "그래, 오래간만이야. 서두르자"),
                ("딸", "할머니 댁! 재밌겠다~"),
                ("강아지", "멍! (신나!)"),
                ("시스템", "방향키로 이동하세요. TAB으로 캐릭터 변경"),
            ],
            1: [
                ("아빠", "와, 이 미술관 정말 크다..."),
                ("엄마", "할머니 댁이 여기서 멀지 않아. 서두르자"),
                ("딸", "저기 뭐가 있는지 내가 먼저 볼게!"),
            ],
            2: [
                ("딸", "엄마, 저기 고미술관이 보여!"),
                ("아빠", "좋아. 따라와"),
                ("시스템", "강아지가 무언가를 발견했습니다! SPACE로 확인"),
            ],
            3: [
                ("아빠", "이 전시물들... 정말 아름답다"),
                ("엄마", "아..., 아빠!"),
                ("아빠", "괜찮아... 살짝 다쳤을 뿐이야"),
                ("시스템", "아빠가 다쳤습니다! 엄마의 치료가 필요합니다"),
            ],
            4: [
                ("엄마", "아빠, 괜찮아? 많이 다쳤어..."),
                ("아빠", "괜찮아... 딸이랑 엄마가 잘 따라와"),
                ("딸", "아빠! 힘내!"),
                ("강아지", "멍... (걱정)"),
            ],
            5: [
                ("아빠", "거의 다 왔어...!"),
                ("엄마", "아빠는 여기서 기다려. 내가 먼저 가서 할머니를 모실게"),
                ("아빠", "미안... 내가 먼저 가야 했는데..."),
                ("딸", "아빠는 여기서 쉴 거야. 우리 곧 올게"),
            ],
            "ending_good": [
                ("시스템", "가족이 할머니 댁에 도착했습니다..."),
                ("엄마", "와, 할머니!"),
                ("할머니", "와, 우리 가족! 오래간만이야"),
                ("딸", "할머니~!"),
                ("시스템", "하지만 아빠는 병원에서 쉬고 있습니다..."),
            ],
            "ending_sad": [
                ("시스템", "아빠는 도착하지 못했습니다..."),
                ("엄마", "아빠는... 우리를 위해..."),
                ("딸", "아빠는 어디야...?"),
                ("시스템", "아빠는 그 길을 떠나갔습니다."),
            ],
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
                        self.cur_w, self.cur_h = FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT
                    else:
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                        self.cur_w, self.cur_h = WINDOW_WIDTH, WINDOW_HEIGHT

                # ✅ 수정: ESC가 intro/ending 상태에서도 작동하지 않도록
                if event.key == pygame.K_ESCAPE and self.state == "playing":
                    self.state = "paused"

                if self.state == "playing":
                    if event.key == pygame.K_TAB:
                        self.family[self.current_member].is_controlled = False
                        self.current_member = (self.current_member + 1) % len(self.family)
                        self.family[self.current_member].is_controlled = True

                    if event.key == pygame.K_SPACE:
                        self.check_ability()

                # ✅ 수정: intro와 ending 모두 SPACE/ENTER로 진행
                if self.state in ["intro", "dialog", "ending"]:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.next_dialog()

                if self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.__init__()

                if self.state == "paused":
                    if event.key == pygame.K_c:
                        self.state = "playing"
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        return False

        return True

    def check_ability(self):
        member = self.family[self.current_member]
        if member.role == "dog":
            if random.random() < 0.4:
                self.secret_items_found += 1
                # ✅ 추가: 발견 피드백 메시지
                print(f"[강아지] 무언가를 발견했어요! ({self.secret_items_found}/{self.required_items})")

    def next_dialog(self):
        if self.current_dialog is None:
            return

        self.dialog_index += 1
        if self.dialog_index >= len(self.current_dialog):
            self.dialog_index = 0
            self.current_dialog = None
            if self.state == "intro":
                self.state = "playing"
                self.family[0].is_controlled = True
            elif self.state == "dialog":
                self.story_progress += 1
                if self.story_progress >= 6:
                    self.trigger_ending()
                else:
                    self.state = "playing"
            elif self.state == "ending":
                self.state = "game_over"

    def trigger_ending(self):
        if self.family[0].hp > 30:
            self.ending_type = "good"
            self.current_dialog = self.dialogs["ending_good"]
        else:
            self.ending_type = "sad"
            self.current_dialog = self.dialogs["ending_sad"]
        self.state = "ending"
        self.dialog_index = 0

    def update(self):
        if self.state == "playing":
            self.game_time += 1

            for member in self.family:
                if member.is_controlled:
                    member.update(room=self.rooms[self.current_room_index])
                else:
                    leader = self.family[self.current_member]
                    member.update(leader.world_pos, self.rooms[self.current_room_index])

            # ✅ 수정: 아빠 아닐 때만 체력 감소
            if self.current_member != 0:
                if self.game_time % 300 == 0:
                    self.family[0].hp = max(0, self.family[0].hp - 2)

            if self.game_time >= self.max_time:
                self.ending_type = "sad"
                self.current_dialog = self.dialogs["ending_sad"]
                self.state = "ending"
                self.dialog_index = 0

            if self.family[0].hp <= 0:
                self.ending_type = "sad"
                self.current_dialog = self.dialogs["ending_sad"]
                self.state = "ending"
                self.dialog_index = 0

            cam_iso = (self.family[self.current_member].world_pos.x - self.family[self.current_member].world_pos.y,
                      (self.family[self.current_member].world_pos.x + self.family[self.current_member].world_pos.y) / 2)
            self.cam_off = (self.cur_w // 2 - cam_iso[0], self.cur_h // 2 - cam_iso[1])

            leader = self.family[self.current_member]
            room = self.rooms[self.current_room_index]
            room_right_edge = (room.floor_area["x"] + room.floor_area["w"]) * TILE_SIZE - 100

            if leader.world_pos.x > room_right_edge and self.current_room_index < len(self.rooms) - 1:
                self.current_room_index += 1
                next_room = self.rooms[self.current_room_index]
                
                if next_room.is_transition:
                    self.trigger_ending()
                else:
                    if next_room.rendered_surface is None:
                        next_room.pre_render(TILE_SIZE)
                    start_x = next_room.floor_area["x"] * TILE_SIZE + 200
                    start_y = (next_room.floor_area["y"] + next_room.floor_area["h"] // 2) * TILE_SIZE
                    
                    for member in self.family:
                        member.world_pos.x = start_x
                        member.world_pos.y = start_y

    def draw_room(self, room):
        if room.rendered_surface is None:
            room.pre_render(TILE_SIZE)

        floor = room.floor_area
        base_x = floor["x"] * TILE_SIZE - floor["y"] * TILE_SIZE
        base_y = (floor["x"] + floor["y"]) * TILE_SIZE // 2

        offset_x = self.cam_off[0] - base_x + 50
        offset_y = self.cam_off[1] - base_y + 50

        self.screen.blit(room.rendered_surface, (offset_x, offset_y))

    def draw_ui(self):
        pygame.draw.rect(self.screen, (20, 20, 25), (0, 0, self.cur_w, 50))
        pygame.draw.rect(self.screen, (40, 40, 50), (0, 50, self.cur_w, 2))

        time_left = max(0, (self.max_time - self.game_time) // 60)
        time_text = self.font.render(f"남은 시간: {time_left}초", True, COLOR_TIMER)
        self.screen.blit(time_text, (20, 15))

        room = self.rooms[self.current_room_index]
        room_text = self.font.render(f"장소: {room.name}", True, COLOR_TEXT)
        self.screen.blit(room_text, (200, 15))

        items_text = self.font.render(f"발견한 것: {self.secret_items_found}/{self.required_items}", True, COLOR_TEXT)
        self.screen.blit(items_text, (450, 15))

        pygame.draw.rect(self.screen, COLOR_HP_BG, (self.cur_w - 220, 10, 200, 30))
        hp_percent = max(0, self.family[0].hp / self.family[0].max_hp)
        pygame.draw.rect(self.screen, COLOR_HP_BAR, (self.cur_w - 220, 10, 200 * hp_percent, 30))
        hp_text = self.font.render("아빠", True, (255, 255, 255))
        self.screen.blit(hp_text, (self.cur_w - 150, 15))

        y_offset = 60
        for i, member in enumerate(self.family):
            color = (100, 255, 100) if i == self.current_member else (150, 150, 150)
            if member.hp < 50:
                color = (255, 150, 150)

            name_text = self.font_small.render(f"{member.name} ({member.ability_name})", True, color)
            self.screen.blit(name_text, (10, y_offset))
            y_offset += 22

        help_text = self.font_small.render("TAB: 캐릭터 변경 | SPACE: 능력 사용 | ESC: 일시정지", True, (150, 150, 150))
        self.screen.blit(help_text, (self.cur_w - 350, self.cur_h - 30))

    def draw_dialog(self):
        if not self.current_dialog:
            return

        speaker, text = self.current_dialog[self.dialog_index]

        dialog_h = 150
        dialog_surface = pygame.Surface((self.cur_w, dialog_h), pygame.SRCALPHA)
        dialog_surface.fill((0, 0, 0, 220))
        self.screen.blit(dialog_surface, (0, self.cur_h - dialog_h))

        speaker_color = (255, 200, 100) if speaker == "시스템" else (200, 200, 255)
        if speaker in ["아빠", "엄마", "딸", "강아지", "할머니"]:
            speaker_color = {
                "아빠": (100, 200, 255),
                "엄마": (255, 150, 150),
                "딸": (150, 255, 150),
                "강아지": (200, 200, 200),
                "할머니": (255, 200, 150)
            }.get(speaker, (200, 200, 255))

        speaker_text = self.font.render(f"{speaker}:", True, speaker_color)
        self.screen.blit(speaker_text, (30, self.cur_h - dialog_h + 20))

        content_text = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(content_text, (30, self.cur_h - dialog_h + 55))

        continue_text = self.font_small.render(" SPACE나 ENTER를 눌러 계속 ", True, (150, 150, 150))
        continue_rect = continue_text.get_rect(right=self.cur_w - 30, bottom=self.cur_h - 15)
        self.screen.blit(continue_text, continue_rect)

    def draw_intro(self):
        self.screen.fill((10, 10, 20))

        title = self.font_title.render("그리운 집으로", True, (255, 220, 150))
        title_rect = title.get_rect(center=(self.cur_w // 2, self.cur_h // 3))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("가족 여정", True, (200, 200, 220))
        subtitle_rect = subtitle.get_rect(center=(self.cur_w // 2, self.cur_h // 3 + 50))
        self.screen.blit(subtitle, subtitle_rect)

        story = self.font_small.render("아빠, 엄마, 딸, 강아지.", True, (180, 180, 180))
        self.screen.blit(story, (self.cur_w // 2 - 100, self.cur_h // 2))

        story2 = self.font_small.render("할머니 댁까지 가는 여정.", True, (180, 180, 180))
        self.screen.blit(story2, (self.cur_w // 2 - 110, self.cur_h // 2 + 30))

        story3 = self.font_small.render("돌아올 수 없는, 하지만 소중한 시간.", True, (180, 180, 180))
        self.screen.blit(story3, (self.cur_w // 2 - 140, self.cur_h // 2 + 60))

        start_text = self.font.render("SPACE를 눌러 시작하세요", True, (255, 255, 100))
        start_rect = start_text.get_rect(center=(self.cur_w // 2, self.cur_h * 3 // 4))
        self.screen.blit(start_text, start_rect)
        
        if self.current_dialog:
            self.draw_dialog()

    def draw_game_over(self):
        overlay = pygame.Surface((self.cur_w, self.cur_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        if self.ending_type == "good":
            title = self.font_title.render("도착", True, (150, 255, 150))
        else:
            title = self.font_title.render("이별", True, (255, 150, 150))

        title_rect = title.get_rect(center=(self.cur_w // 2, self.cur_h // 3))
        self.screen.blit(title, title_rect)

        restart_text = self.font.render("R을 눌러 다시 시작", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.cur_w // 2, self.cur_h // 2))
        self.screen.blit(restart_text, restart_rect)

    def draw_paused(self):
        overlay = pygame.Surface((self.cur_w, self.cur_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font_title.render("일시정지", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.cur_w // 2, self.cur_h // 3))
        self.screen.blit(pause_text, pause_rect)

        cont_text = self.font.render("C: 계속하기", True, (200, 200, 200))
        cont_rect = cont_text.get_rect(center=(self.cur_w // 2, self.cur_h // 2))
        self.screen.blit(cont_text, cont_rect)

        quit_text = self.font.render("Q: 종료하기", True, (200, 200, 200))
        quit_rect = quit_text.get_rect(center=(self.cur_w // 2, self.cur_h // 2 + 40))
        self.screen.blit(quit_text, quit_rect)

    def draw_ending(self):
        self.screen.fill((5, 5, 10))

        for i, member in enumerate(self.family):
            member.draw(self.screen, (self.cur_w // 2 + (i - 1.5) * 80, self.cur_h // 2))

        if self.current_dialog and self.dialog_index < len(self.current_dialog):
            dialog_h = 120
            dialog_surface = pygame.Surface((self.cur_w, dialog_h), pygame.SRCALPHA)
            dialog_surface.fill((0, 0, 0, 230))
            self.screen.blit(dialog_surface, (0, self.cur_h - dialog_h))

            speaker, text = self.current_dialog[self.dialog_index]

            speaker_color = (255, 200, 100) if speaker == "시스템" else (200, 200, 255)
            if speaker == "할머니":
                speaker_color = (255, 200, 150)
            
            speaker_text = self.font.render(f"{speaker}:", True, speaker_color)
            self.screen.blit(speaker_text, (30, self.cur_h - dialog_h + 20))

            content_text = self.font.render(text, True, COLOR_TEXT)
            self.screen.blit(content_text, (30, self.cur_h - dialog_h + 55))

            continue_text = self.font_small.render(" SPACE나 ENTER를 눌러 계속 ", True, (150, 150, 150))
            continue_rect = continue_text.get_rect(right=self.cur_w - 30, bottom=self.cur_h - 15)
            self.screen.blit(continue_text, continue_rect)

    def draw(self):
        self.screen.fill(COLOR_OUTSIDE)

        if self.state == "intro":
            self.draw_intro()
        elif self.state == "playing":
            self.draw_room(self.rooms[self.current_room_index])

            for member in self.family:
                member.draw(self.screen, self.cam_off)

            self.draw_ui()
            self.draw_dialog()
        elif self.state == "dialog":
            self.draw_room(self.rooms[self.current_room_index])

            for member in self.family:
                member.draw(self.screen, self.cam_off)

            self.draw_ui()
            self.draw_dialog()
        elif self.state == "ending":
            self.draw_ending()
        elif self.state == "game_over":
            self.draw_room(self.rooms[self.current_room_index])
            for member in self.family:
                member.draw(self.screen, self.cam_off)
            self.draw_game_over()
        elif self.state == "paused":
            self.draw_room(self.rooms[self.current_room_index])
            for member in self.family:
                member.draw(self.screen, self.cam_off)
            self.draw_ui()
            self.draw_paused()

        pygame.display.flip()

    def start_intro(self):
        self.current_dialog = self.dialogs[0]
        self.dialog_index = 0
        self.state = "intro"

    def run(self):
        self.start_intro()

        running = True
        while running:
            running = self.handle_events()
            if running:
                self.update()
                self.draw()
                self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except pygame.error as e:
        print(f"Pygame 에러 발생: {e}")
    except Exception as e:
        print(f"기타 에러 발생: {e}")
    finally:
        pygame.quit()