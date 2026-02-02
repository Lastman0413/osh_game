import pygame
import sys

# --- 초기 설정 ---
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60

# 색상 정의
COLOR_BG = (30, 30, 35)           # 배경 (어두운 회색)
COLOR_TITLE = (255, 255, 255)      # 제목 (흰색)
COLOR_MENU_NORMAL = (200, 200, 200)  # 메뉴 기본
COLOR_MENU_HOVER = (255, 220, 100)   # 메뉴 호버 (노란색)
COLOR_MENU_BG = (50, 50, 55)       # 메뉴 배경
COLOR_MENU_BG_HOVER = (70, 70, 80) # 메뉴 배경 호버

class MenuItem:
    def __init__(self, text, y_pos, action):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(0, y_pos, 400, 60)
        self.rect.centerx = WINDOW_WIDTH // 2
        self.is_hovered = False
        
    def update(self, mouse_pos):
        """마우스 호버 체크"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface, font):
        """메뉴 아이템 그리기"""
        # 배경
        bg_color = COLOR_MENU_BG_HOVER if self.is_hovered else COLOR_MENU_BG
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_MENU_NORMAL, self.rect, 2, border_radius=10)
        
        # 텍스트
        text_color = COLOR_MENU_HOVER if self.is_hovered else COLOR_MENU_NORMAL
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def click(self):
        """클릭 시 액션 실행"""
        if self.is_hovered:
            print(f"[메뉴 클릭] {self.text} → {self.action}")
            return self.action
        return None

class MainMenu:
    def __init__(self):
        # 한글 지원 폰트 (시스템 폰트 사용)
        try:
            # Windows: 맑은 고딕
            self.font_title = pygame.font.SysFont('malgungothic', 72)
            self.font_menu = pygame.font.SysFont('malgungothic', 48)
            self.font_small = pygame.font.SysFont('malgungothic', 24)
        except:
            # 맑은 고딕 없으면 다른 한글 폰트 시도
            try:
                self.font_title = pygame.font.SysFont('nanumgothic', 72)
                self.font_menu = pygame.font.SysFont('nanumgothic', 48)
                self.font_small = pygame.font.SysFont('nanumgothic', 24)
            except:
                # 그래도 없으면 아무 한글 폰트
                available_fonts = pygame.font.get_fonts()
                korean_fonts = [f for f in available_fonts if 'gothic' in f or 'malgun' in f or 'nanum' in f]
                if korean_fonts:
                    self.font_title = pygame.font.SysFont(korean_fonts[0], 72)
                    self.font_menu = pygame.font.SysFont(korean_fonts[0], 48)
                    self.font_small = pygame.font.SysFont(korean_fonts[0], 24)
                else:
                    # 최후의 수단: 기본 폰트
                    self.font_title = pygame.font.Font(None, 72)
                    self.font_menu = pygame.font.Font(None, 48)
                    self.font_small = pygame.font.Font(None, 24)
        
        # 메뉴 아이템들
        menu_start_y = 200
        menu_spacing = 80
        
        self.menu_items = [
            MenuItem("새 게임", menu_start_y + menu_spacing * 0, "new_game"),
            MenuItem("이어하기", menu_start_y + menu_spacing * 1, "continue"),
            MenuItem("추억의 가족사진첩", menu_start_y + menu_spacing * 2, "album"),
            MenuItem("모드 추가", menu_start_y + menu_spacing * 3, "mods"),
            MenuItem("끝내기", menu_start_y + menu_spacing * 4, "quit")
        ]
        
        self.title = "할머니 집으로"
        self.subtitle = "A Family's Journey"
        
    def update(self, mouse_pos):
        """마우스 위치에 따라 메뉴 업데이트"""
        for item in self.menu_items:
            item.update(mouse_pos)
    
    def draw(self, surface):
        """메뉴 화면 그리기"""
        # 배경
        surface.fill(COLOR_BG)
        
        # 제목
        title_surface = self.font_title.render(self.title, True, COLOR_TITLE)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))
        surface.blit(title_surface, title_rect)
        
        # 부제목
        subtitle_surface = self.font_small.render(self.subtitle, True, COLOR_MENU_NORMAL)
        subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, 150))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # 메뉴 아이템들
        for item in self.menu_items:
            item.draw(surface, self.font_menu)
        
        # 하단 정보
        info_text = "WASD: 이동 | F: 전체화면 | ESC: 메뉴"
        info_surface = self.font_small.render(info_text, True, (100, 100, 100))
        info_rect = info_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        surface.blit(info_surface, info_rect)
    
    def handle_click(self, mouse_pos):
        """클릭 처리"""
        for item in self.menu_items:
            action = item.click()
            if action:
                return action
        return None

def handle_menu_action(action):
    """메뉴 액션 처리"""
    if action == "new_game":
        print("\n=== 새 게임 시작 ===")
        print("게임 메인으로 전환...")
        # 여기에 게임 시작 코드 연결
        return "start_game"
    
    elif action == "continue":
        print("\n=== 이어하기 ===")
        print("세이브 파일 로드 중...")
        # 여기에 로드 코드 연결
        return "load_game"
    
    elif action == "album":
        print("\n=== 추억의 가족사진첩 ===")
        print("사진첩 화면으로 전환...")
        # 여기에 사진첩 화면 연결
        return "show_album"
    
    elif action == "mods":
        print("\n=== 모드 추가 ===")
        print("모드 관리 화면으로 전환...")
        # 여기에 모드 관리 화면 연결
        return "show_mods"
    
    elif action == "quit":
        print("\n=== 게임 종료 ===")
        return "quit"
    
    return None

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("할머니 집으로 - 메인 메뉴")
    clock = pygame.time.Clock()
    
    menu = MainMenu()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 왼클릭
                    action = menu.handle_click(mouse_pos)
                    if action:
                        result = handle_menu_action(action)
                        if result == "quit":
                            pygame.quit()
                            sys.exit()
                        elif result == "start_game":
                            print("→ 여기서 게임 메인 코드로 전환!")
                            # return "start_game"  # 나중에 메인 게임과 연결
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # 업데이트
        menu.update(mouse_pos)
        
        # 그리기
        menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()