import json
import math
import os
import random
import pygame

# Pygame 초기화
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("동일률과 모순률")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GRAY = (100, 100, 100)
GREEN = (50, 255, 50)

# 세이브 파일 경로
SAVE_FILE = "game_save.json"


def load_data():
  if os.path.exists(SAVE_FILE):
    try:
      with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  return {
      "points": 100,  # 처음에 시작할 때 주는 100포인트
      "unlocked": {"동일률": False, "모순률": False},
      "equipped": None,
      "upgrades": {"speed": 0, "damage": 0},
  }


def save_data(data):
  with open(SAVE_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


game_data = load_data()


# 폰트 설정 (한글 렌더링)
def get_font(size):
  return pygame.font.SysFont("malgungothic", size)


font_large = get_font(36)
font_med = get_font(24)
font_small = get_font(18)

# 게임 상태 관리
state = "MENU"
reset_step = 0  # 5번의 동의에 걸친 데이터 초기화 단계


class Player:

  def __init__(self, char_type):
    self.x = SCREEN_WIDTH // 2
    self.y = SCREEN_HEIGHT // 2
    self.radius = 15
    self.char_type = char_type
    self.speed = 4 + game_data["upgrades"]["speed"] * 0.5
    self.hp = 100

  def move(self, keys):
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
      self.x -= self.speed
    if keys[pygame.K_right] or keys[pygame.K_d]:
      self.x += self.speed
    if keys[pygame.K_up] or keys[pygame.K_w]:
      self.y -= self.speed
    if keys[pygame.K_down] or keys[pygame.K_s]:
      self.y += self.speed

    self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
    self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

  def draw(self):
    # 동일률은 하얀색 2D 원, 모순률은 노란색 2D 원
    color = WHITE if self.char_type == "동일률" else YELLOW
    pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
    pygame.draw.circle(
        screen, BLACK, (int(self.x), int(self.y)), self.radius, 2
    )


class Enemy:

  def __init__(self, px, py):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.randint(400, 600)
    self.x = px + math.cos(angle) * dist
    self.y = py + math.sin(angle) * dist
    self.radius = 10
    self.speed = 2
    self.hp = 10 + game_data["upgrades"]["damage"] * 5

  def move(self, px, py):
    angle = math.atan2(py - self.y, px - self.x)
    self.x += math.cos(angle) * self.speed
    self.y += math.sin(angle) * self.speed

  def draw(self):
    pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)


class Projectile:

  def __init__(self, x, y, angle):
    self.x = x
    self.y = y
    self.speed = 8
    self.vx = math.cos(angle) * self.speed
    self.vy = math.sin(angle) * self.speed
    self.radius = 5

  def update(self):
    self.x += self.vx
    self.y += self.vy

  def draw(self):
    pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius)


player = None
enemies = []
projectiles = []
spawn_timer = 0
score_earned_in_run = 0
attack_cooldown = 0


def reset_game():
  global player, enemies, projectiles, spawn_timer, score_earned_in_run
  if not game_data["equipped"]:
    return False
  player = Player(game_data["equipped"])
  enemies = []
  projectiles = []
  spawn_timer = 0
  score_earned_in_run = 0
  return True


running = True
while running:
  screen.fill(BLACK)
  keys = pygame.key.get_pressed()

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.KEYDOWN:
      if state == "MENU":
        if event.key == pygame.K_1:
          # 본격적인 플레이 (장착된 캐릭터가 없으면 불가능)
          if game_data["equipped"] is not None:
            if reset_game():
              state = "PLAYING"
        elif event.key == pygame.K_2:
          state = "CHARACTER"
        elif event.key == pygame.K_3:
          state = "UPGRADE"
        elif event.key == pygame.K_4:
          state = "RESET"
          reset_step = 0
        elif event.key == pygame.K_5:
          running = False

      elif state == "CHARACTER":
        if event.key == pygame.K_1:
          # 동일률: 100포인트로 구매, 장착
          if game_data["unlocked"]["동일률"]:
            game_data["equipped"] = "동일률"
            save_data(game_data)
          else:
            if game_data["points"] >= 100:
              game_data["points"] -= 100
              game_data["unlocked"]["동일률"] = True
              game_data["equipped"] = "동일률"
              save_data(game_data)
        elif event.key == pygame.K_2:
          # 모순률: 500포인트로 구매, 장착
          if game_data["unlocked"]["모순률"]:
            game_data["equipped"] = "모순률"
            save_data(game_data)
          else:
            if game_data["points"] >= 500:
              game_data["points"] -= 500
              game_data["unlocked"]["모순률"] = True
              game_data["equipped"] = "모순률"
              save_data(game_data)
        elif event.key == pygame.K_ESCAPE:
          state = "MENU"

      elif state == "UPGRADE":
        if event.key == pygame.K_1:
          if game_data["points"] >= 50:
            game_data["points"] -= 50
            game_data["upgrades"]["speed"] += 1
            save_data(game_data)
        elif event.key == pygame.K_2:
          if game_data["points"] >= 50:
            game_data["points"] -= 50
            game_data["upgrades"]["damage"] += 1
            save_data(game_data)
        elif event.key == pygame.K_ESCAPE:
          state = "MENU"

      elif state == "RESET":
        if event.key == pygame.K_y:
          reset_step += 1
          if reset_step >= 5:
            game_data = {
                "points": 100,
                "unlocked": {"동일률": False, "모순률": False},
                "equipped": None,
                "upgrades": {"speed": 0, "damage": 0},
            }
            save_data(game_data)
            reset_step = 0
            state = "MENU"
        else:
          if event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            reset_step = 0
            state = "MENU"

      elif state == "PLAYING":
        if event.key == pygame.K_ESCAPE:
          state = "MENU"

      elif state == "GAME_OVER":
        if event.key == pygame.K_RETURN:
          game_data["points"] += score_earned_in_run
          save_data(game_data)
          state = "MENU"

  # 화면 렌더링 및 로직 처리
  if state == "MENU":
    title = font_large.render("동일률과 모순률 (뱀서류 게임)", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    equipped_status = (
        game_data["equipped"] if game_data["equipped"] else "없음 (장착 필수)"
    )
    eq_text = font_med.render(
        f"장착된 캐릭터: {equipped_status}",
        True,
        WHITE if game_data["equipped"] else RED,
    )
    screen.blit(eq_text, (SCREEN_WIDTH // 2 - eq_text.get_width() // 2, 130))

    p_text = font_med.render(f"보유 포인트: {game_data['points']}", True, GREEN)
    screen.blit(p_text, (SCREEN_WIDTH // 2 - p_text.get_width() // 2, 170))

    m1 = font_med.render(
        "1. 게임 시작 (장착된 캐릭터 필요)",
        True,
        WHITE if game_data["equipped"] else GRAY,
    )
    m2 = font_med.render("2. 캐릭터 선택 및 구매 상점", True, WHITE)
    m3 = font_med.render("3. 포인트 업그레이드", True, WHITE)
    m4 = font_med.render("4. 데이터 초기화 (5번 동의 필요)", True, WHITE)
    m5 = font_med.render("5. 게임 종료", True, WHITE)

    for i, t_surface in enumerate([m1, m2, m3, m4, m5]):
      screen.blit(
          t_surface, (SCREEN_WIDTH // 2 - t_surface.get_width() // 2, 240 + i * 50)
      )

    if not game_data["equipped"]:
      warn = font_small.render(
          "※ 플레이어의 아무런 캐릭터를 장착하기 전에는 본격적인 플레이가 불가능합니다!",
          True,
          RED,
      )
      screen.blit(warn, (SCREEN_WIDTH // 2 - warn.get_width() // 2, 510))

  elif state == "CHARACTER":
    title = font_large.render("캐릭터 선택 / 상점", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

    p_text = font_med.render(f"보유 포인트: {game_data['points']}", True, GREEN)
    screen.blit(p_text, (SCREEN_WIDTH // 2 - p_text.get_width() // 2, 110))

    # 동일률 (1번째, 하얀색 원, 100포인트)
    d_state = (
        "장착 중"
        if game_data["equipped"] == "동일률"
        else (
            "보유 중 (장착하기)"
            if game_data["unlocked"]["동일률"]
            else "구매 (100 포인트)"
        )
    )
    c1 = font_med.render(f"1. 동일률 (하얀색 2D 원): {d_state}", True, WHITE)

    # 모순률 (2번째, 노란색 원, 500포인트, 적 처치시 10포인트)
    m_state = (
        "장착 중"
        if game_data["equipped"] == "모순률"
        else (
            "보유 중 (장착하기)"
            if game_data["unlocked"]["모순률"]
            else "구매 (500 포인트 - 적 처치 시 10P)"
        )
    )
    c2 = font_med.render(f"2. 모순률 (노란색 2D 원): {m_state}", True, YELLOW)

    screen.blit(c1, (SCREEN_WIDTH // 2 - c1.get_width() // 2, 200))
    screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2, 260))

    esc = font_small.render("ESC: 메인 메뉴", True, GRAY)
    screen.blit(esc, (SCREEN_WIDTH // 2 - esc.get_width() // 2, 450))

  elif state == "UPGRADE":
    title = font_large.render("포인트 업그레이드", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

    p_text = font_med.render(f"보유 포인트: {game_data['points']}", True, GREEN)
    screen.blit(p_text, (SCREEN_WIDTH // 2 - p_text.get_width() // 2, 110))

    u1 = font_med.render(
        f"1. 이동 속도 증가 (비용: 50P) - 레벨: {game_data['upgrades']['speed']}",
        True,
        WHITE,
    )
    u2 = font_med.render(
        f"2. 공격력 증가 (비용: 50P) - 레벨: {game_data['upgrades']['damage']}",
        True,
        WHITE,
    )

    screen.blit(u1, (SCREEN_WIDTH // 2 - u1.get_width() // 2, 200))
    screen.blit(u2, (SCREEN_WIDTH // 2 - u2.get_width() // 2, 260))

    esc = font_small.render("ESC: 메인 메뉴", True, GRAY)
    screen.blit(esc, (SCREEN_WIDTH // 2 - esc.get_width() // 2, 450))

  elif state == "RESET":
    title = font_large.render("데이터 초기화 확인", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    msg = font_med.render(
        f"초기화 동의 진행 중: {reset_step} / 5 단계", True, WHITE
    )
    screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 200))

    desc = font_small.render(
        "Y 키를 누르면 동의 횟수가 증가합니다. (총 5번 필요, 다른 키는 취소)",
        True,
        GRAY,
    )
    screen.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, 260))

  elif state == "PLAYING":
    player.move(keys)

    # 뱀서류 자동 공격 시스템
    attack_cooldown += 1
    if attack_cooldown >= 30:
      attack_cooldown = 0
      if enemies:
        closest = min(
            enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y)
        )
        angle = math.atan2(closest.y - player.y, closest.x - player.x)
        projectiles.append(Projectile(player.x, player.y, angle))

    for p in projectiles[:]:
      p.update()
      if p.x < 0 or p.x > SCREEN_WIDTH or p.y < 0 or p.y > SCREEN_HEIGHT:
        projectiles.remove(p)

    spawn_timer += 1
    if spawn_timer >= 40:
      spawn_timer = 0
      enemies.append(Enemy(player.x, player.y))

    for e in enemies[:]:
      e.move(player.x, player.y)
      if math.hypot(player.x - e.x, player.y - e.y) < player.radius + e.radius:
        player.hp -= 1
        if player.hp <= 0:
          state = "GAME_OVER"

      for p in projectiles[:]:
        if math.hypot(p.x - e.x, p.y - e.y) < p.radius + e.radius:
          if p in projectiles:
            projectiles.remove(p)
          e.hp -= 10 + game_data["upgrades"]["damage"] * 5
          if e.hp <= 0:
            if e in enemies:
              enemies.remove(e)
            # 모순률은 적을 죽이면 10포인트 획득
            if player.char_type == "모순률":
              score_earned_in_run += 10
            else:
              score_earned_in_run += 2
          break

    player.draw()
    for e in enemies:
      e.draw()
    for p in projectiles:
      p.draw()

    hp_text = font_small.render(f"HP: {player.hp}", True, RED)
    score_text = font_small.render(
        f"이번 판 획득 포인트: {score_earned_in_run}", True, GREEN
    )
    char_text = font_small.render(f"캐릭터: {player.char_type}", True, WHITE)
    screen.blit(hp_text, (10, 10))
    screen.blit(score_text, (10, 30))
    screen.blit(char_text, (10, 50))

  elif state == "GAME_OVER":
    go_title = font_large.render("게임 오버", True, RED)
    res_text = font_med.render(
        f"획득한 포인트 저장: +{score_earned_in_run}P", True, GREEN
    )
    ret_text = font_small.render(
        "ENTER 키를 누르면 메인 메뉴로 돌아갑니다.", True, WHITE
    )

    screen.blit(go_title, (SCREEN_WIDTH // 2 - go_title.get_width() // 2, 180))
    screen.blit(res_text, (SCREEN_WIDTH // 2 - res_text.get_width() // 2, 260))
    screen.blit(ret_text, (SCREEN_WIDTH // 2 - ret_text.get_width() // 2, 320))

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
