import pygame
import sys
import random

# --- 초기 설정 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Zomboid Style")
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (150, 0, 0)

# 폰트 설정
try:
    font_main = pygame.font.SysFont("malgungothic", 40, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 20)
except:
    font_main = pygame.font.SysFont("arial", 40, bold=True)
    font_small = pygame.font.SysFont("arial", 20)

# --- 상태 관리 ---
STATE_TITLE = "TITLE"
STATE_PROLOGUE = "PROLOGUE"
STATE_GAME = "GAME"
current_state = STATE_TITLE

# --- 버튼 클래스 ---
class Button:
    def __init__(self, text, x, y, width, height, color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        draw_color = (self.color[0]+30, self.color[1]+30, self.color[2]+30) if self.is_hovered else self.color
        pygame.draw.rect(surface, draw_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2) # 테두리
        text_surf = font_small.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

# --- 프롤로그 데이터 ---
prologue_text = [
    "세상은 단 며칠 만에 무너졌다.",
    "이제 도시는 굶주린 시체들로 가득하다.",
    "이것은 당신이 어떻게 죽었는지에 대한 기록이다."
]
prologue_index = 0
last_prologue_time = 0

# 버튼 생성
btn_new_game = Button("새 게임", 400, 300, 200, 50, GRAY)
btn_load_game = Button("이어하기 (준비 중)", 400, 370, 200, 50, GRAY)
btn_exit = Button("나가기", 400, 440, 200, 50, GRAY)

# (이전의 Survivor, Zombie, Bullet 클래스들은 그대로 유지한다고 가정합니다)
# 생략된 클래스 부분은 이전 답변의 코드를 그대로 활용하시면 됩니다.

def draw_title():
    screen.fill(BLACK)
    title_surf = font_main.render("PROJECT ZOMBOID CLONE", True, RED)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 150))
    btn_new_game.draw(screen)
    btn_load_game.draw(screen)
    btn_exit.draw(screen)

def draw_prologue():
    global current_state, prologue_index, last_prologue_time
    screen.fill(BLACK)
    
    # 텍스트 출력
    current_txt = prologue_text[prologue_index]
    txt_surf = font_small.render(current_txt, True, WHITE)
    screen.blit(txt_surf, (SCREEN_WIDTH//2 - txt_surf.get_width()//2, SCREEN_HEIGHT//2))
    
    tip_surf = font_small.render("[ 스페이스바를 눌러 계속 ]", True, (100, 100, 100))
    screen.blit(tip_surf, (SCREEN_WIDTH//2 - tip_surf.get_width()//2, 700))

# --- 메인 루프 ---
while True:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        if current_state == STATE_TITLE:
            btn_new_game.check_hover(mouse_pos)
            btn_load_game.check_hover(mouse_pos)
            btn_exit.check_hover(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_new_game.rect.collidepoint(mouse_pos):
                    current_state = STATE_PROLOGUE
                if btn_exit.rect.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()
                    
        elif current_state == STATE_PROLOGUE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    prologue_index += 1
                    if prologue_index >= len(prologue_text):
                        current_state = STATE_GAME

    # 화면 그리기
    if current_state == STATE_TITLE:
        draw_title()
    elif current_state == STATE_PROLOGUE:
        draw_prologue()
    elif current_state == STATE_GAME:
        # 이전에 만든 게임 로직 실행 (배경, 플레이어, 좀비 등)
        screen.fill((40, 45, 40)) # 임시 배경
        game_msg = font_main.render("게임이 시작되었습니다!", True, WHITE)
        screen.blit(game_msg, (SCREEN_WIDTH//2 - game_msg.get_width()//2, SCREEN_HEIGHT//2))
        # 여기에 이전의 all_sprites.update(), draw() 등을 넣으시면 됩니다.

    pygame.display.flip()
    clock.tick(FPS)