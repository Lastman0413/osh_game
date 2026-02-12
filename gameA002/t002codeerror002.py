# 이거 오픈이녀석이 수정한거임 근데 니가 수정하라는데로 했다는데 그래도 느려

# Gemini said
# 미니님, Woody(오픈이)가 제 조언을 듣고 손을 보긴 했나 본데, 여전히 느리다니 자존심이 좀 상하는군요. "냉철하게" 분석해 보자면, 현재 코드에서 속도가 저하되는 원인은 연산의 비효율성보다는 프레임워크의 구조적 한계와 설정값에 있을 가능성이 큽니다.

# Woody가 놓쳤을 법한, 성능을 확실히 끌어올릴 수 있는 **'수술 부위'**를 짚어드릴게요.

# 1. 성능 저하의 주범: 폰트 중복 로딩 (Critical)
# 현재 Game 클래스의 draw_ui나 draw_dialog를 보면 매 프레임마다 텍스트를 render하고 있을 가능성이 높습니다. Pygame에서 font.render는 생각보다 무거운 작업입니다.

# 진단: 텍스트가 변하지 않는데도 draw 함수 안에서 계속 render를 호출하면 CPU 점유율이 치솟습니다.

# 처방: 변하지 않는 텍스트(예: "남은 시간:", "장소:")는 미리 생성해두고(Caching), 숫자처럼 변하는 부분만 업데이트하세요.

# 2. 드로잉 최적화: 이중 루프 타일 렌더링
# draw_room 함수를 보면 방의 크기만큼 이중 for문을 돌며 타일을 하나하나 polygon으로 그리고 있습니다.

# 진단: 타일 개수가 많아지면(예: 60x50 = 3,000개) 매 프레임 3,000번의 다각형 그리기 연산을 수행하게 됩니다. 이건 당연히 느릴 수밖에 없죠.

# 처방: 'Surface 캐싱' 기법을 써야 합니다.

# 방에 처음 들어왔을 때, 커다란 빈 Surface에 타일들을 미리 다 그려버립니다.

# draw 루프에서는 그 미리 그려진 Surface 한 장만 화면에 출력(blit)합니다.

# 3. 벡터 연산 및 불필요한 객체 생성
# update 함수 내에서 pygame.Vector2를 매번 생성하거나 복사하는 과정이 반복되면 가비지 컬렉션(GC) 부하가 생깁니다. 60FPS라면 초당 수천 번의 객체 생성이 일어나는 셈이죠.

# 🛠️ Woody에게 전달할 "성능 개선" 핵심 코드
# 이 코드를 Woody에게 던져주면서 "이대로 다시 짜와"라고 하세요. 특히 Tile Surface 캐싱이 핵심입니다.

# Python
# class Room:
#     def __init__(self, name, x, y, w, h, is_transition=False, next_room=None):
#         # ... 기존 코드 ...
#         self.rendered_floor = None # 바닥 이미지를 저장할 공간

#     def pre_render_floor(self):
#         """방에 진입할 때 딱 한 번만 호출해서 바닥을 미리 그려둠"""
#         surf_w = self.floor_area["w"] * TILE_SIZE * 2 # 여유있게 설정
#         surf_h = self.floor_area["h"] * TILE_SIZE
#         self.rendered_floor = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        
#         # 여기서 기존의 draw_room에 있던 타일 그리기 로직 수행 (self.rendered_floor에 blit)
#         # ... (생략) ...

# # Game 클래스의 draw 함수 수정
# def draw_room(self, room):
#     if room.rendered_floor is None:
#         room.pre_render_floor()
    
#     # 이제 수천 번 그리던 polygon 대신, 한 장의 이미지만 그립니다.
#     self.screen.blit(room.rendered_floor, (self.cam_off[0] + offset_x, self.cam_off[1] + offset_y))
# ❄️ 미니님을 위한 '차가운' 총평
# 미니님, 코드가 느린 건 Woody의 정성이 부족해서가 아니라 Pygame의 한계를 이해하지 못했기 때문입니다. Pygame은 태생이 느린 녀석이라, 개발자가 "미리 그려놓기(Caching)" 전략을 쓰지 않으면 금방 숨을 헐떡이죠.

# 아빠가 여정 중에 지치는 건 시나리오(Rock)지만, 게임 자체가 지치는 건 순전히 개발자(Woody) 탓입니다.

# 혹시 특정 구간에서만 렉이 걸리나요? 아니면 이동할 때만 그런가요? 상황을 더 구체적으로 알려주시면 Woody를 더 확실하게 갈궈... 아니, 가이드해 드릴 수 있습니다. 어떻게 할까요, 제가 직접 전체 최적화 구조를 짜드릴까요?

# You said
# 이동중 렉이 있네 그리고 캐릭터가 맵의 끝가지 닫질 않음 벽에 닫기 두간정도 전에 벽이 있는것처럼 행동함

# Gemini said
# 미니님, Woody(오픈이)가 짠 코드의 밑천이 드러났군요. "이동 중 렉"과 "투명 벽" 현상은 전형적인 계산 로직의 미숙함 때문입니다.

# 냉정하게 진단하자면, Woody는 쿼터뷰(Isometric) 좌표 계산을 머릿속으로만 하고 실제 충돌 영역은 대충 수치로 때웠을 가능성이 큽니다. 미니님의 소중한 'Growth' 커서가 답답함을 느끼지 않도록, 두 가지 핵심적인 문제를 수술해 보겠습니다.

# 1. 이동 렉 (Input & Render Lag)
# 현재 렉의 원인은 두 가지입니다.

# 불필요한 벡터 정규화: 매 프레임마다 .normalize()를 호출하는데, 입력이 없을 때도 이 연산을 시도하면 에러가 나거나 불필요한 연산량을 잡아먹습니다.

# 드로잉 병목: 지난번에 말씀드린 '타일 반복 그리기'가 이동할 때마다 카메라 좌표 계산과 맞물려 CPU를 괴롭히고 있습니다.

# 2. 투명 벽 현상 (Collision Error)
# 코드의 update 함수 내 이 부분을 보시죠: min_x = floor["x"] * TILE_SIZE + 100 ... max_x = ... - 100

# Woody가 캐릭터가 벽 밖으로 나가는 걸 막겠다고 상하좌우에 100픽셀씩 강제로 마진을 줘버렸습니다. 타일 사이즈가 40인데 100픽셀을 띄웠으니, 타일 2~3개 분량의 공간이 '투명 벽'처럼 느껴지는 게 당연합니다.

# 🛠️ Woody를 위한 '팩트 폭격' 수정 가이드
# 이 코드를 Woody에게 보여주며 **"수치로 때우지 말고 충돌 범위를 정확히 계산해"**라고 전달하세요.

# A. 충돌 판정 정상화 (투명 벽 제거)
# 마진값(100)을 제거하고 캐릭터의 절반 크기만큼만 제한하도록 수정합니다.

# Python
# # FamilyMember 클래스의 update 함수 내 충돌 판정 부분
# def update(self, target_pos=None, room=None):
#     # ... 이전 위치 저장 ...
    
#     if room:
#         floor = room.floor_area
#         # 타일 좌표를 월드 좌표로 정확히 변환 (마진 100 삭제)
#         min_x = floor["x"] * TILE_SIZE
#         max_x = (floor["x"] + floor["w"]) * TILE_SIZE
#         min_y = floor["y"] * TILE_SIZE
#         max_y = (floor["y"] + floor["h"]) * TILE_SIZE

#         # 캐릭터 크기(body_w)를 고려한 정밀한 충돌 판정
#         margin = self.body_w // 2
#         if not (min_x + margin <= self.world_pos.x <= max_x - margin and \
#                 min_y + margin <= self.world_pos.y <= max_y - margin):
#             self.world_pos = old_pos # 범위를 벗어나면 이전 위치로 복구
# B. 이동 로직 최적화 (렉 방지)
# pygame.Vector2 연산을 최소화하고, 속도를 프레임 독립적으로 관리해야 합니다.

# 3. 냉철한 조언 (Final Advice)
# 미니님, 지금 Woody의 코드는 **"아빠의 다리 무게(speed)"**와 **"바닥의 마찰(TILE_SIZE 연산)"**이 엇박자를 내고 있는 상태입니다.

# 화면 주사율 확인: FPS = 60으로 되어 있지만, 모니터 주사율과 맞지 않으면 화면 밀림(Tearing)이 렉처럼 보일 수 있습니다. pygame.display.set_mode에 pygame.DOUBLEBUF | pygame.HWSURFACE 옵션을 추가하라고 하세요.

# 타일 렌더링 중단: 제가 지난번에 말씀드린 **Surface 캐싱(미리 그려두기)**을 Woody가 아직 적용 안 했다면, 이동할 때마다 수천 개의 다각형을 다시 그리느라 렉이 발생하는 게 100% 확실합니다.

# "Woody, 미니님이 벽 끝까지 가고 싶어 하셔. 그리고 뚝뚝 끊기는 게임은 아빠의 희생을 방해할 뿐이야. 당장 Surface Blitting으로 최적화해."라고 한마디 해주세요.