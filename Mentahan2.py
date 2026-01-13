import pygame
import sys
import random
import time
import csv
import os

pygame.init()

# ================== WINDOW ==================
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Memori Warna")

# ================== COLORS ==================
BG = (235, 245, 255)
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)

RED = (255, 99, 132)
GREEN = (75, 192, 192)
BLUE = (54, 162, 235)
YELLOW = (255, 206, 86)

BTN = (180, 215, 255)
BTN_HOVER = (140, 195, 255)

colors = {
    "MERAH": RED,
    "HIJAU": GREEN,
    "BIRU": BLUE,
    "KUNING": YELLOW
}

# ================== FONT ==================
font_title = pygame.font.SysFont("comic sans ms", 56, bold=True)
font_big = pygame.font.SysFont("comic sans ms", 42)
font_small = pygame.font.SysFont("comic sans ms", 28)

clock = pygame.time.Clock()

# ================== CSV ==================
CSV_FILE = "hasil_penelitian_memori.csv"
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow(
            ["Nama", "Level", "Urutan", "Jawaban", "Hasil", "Waktu"]
        )

# ================== GAME VAR ==================
state = "MENU"
player_name = ""
level_name = ""
base_length = 3
sequence = []
user_input = []
selected_color = ""
start_time = 0
reaction_time = 0
message = ""
fireworks = []
show_fireworks = False


# ================== UI FUNCTION ==================
def draw_text(text, y, font, color=BLACK):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH // 2, y))
    screen.blit(render, rect)

def draw_button(rect, text):
    mouse = pygame.mouse.get_pos()
    color = BTN_HOVER if rect.collidepoint(mouse) else BTN

    pygame.draw.rect(screen, color, rect, border_radius=20)

    text_surface = font_small.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def generate_sequence(length):
    return random.sample(list(colors.keys()), length)

def save_data(result):
    with open(CSV_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            player_name,
            level_name,
            " - ".join(sequence),
            " - ".join(user_input),
            result,
            round(reaction_time, 2)
        ])

def draw_color_buttons():
    buttons = {}
    size = 120
    gap = 160
    x_start = 120
    y = 360

    for i, (name, color) in enumerate(colors.items()):
        rect = pygame.Rect(x_start + i * gap, y, size, size)
        pygame.draw.rect(screen, color, rect, border_radius=25)

        if name == selected_color:
            pygame.draw.rect(screen, BLACK, rect, 4, border_radius=25)

        buttons[name] = rect
    return buttons
class FireworkParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 6)
        self.color = random.choice([
            RED, GREEN, BLUE, YELLOW
        ])
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = 40

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(self.y)),
                self.radius
            )


# ================== MAIN LOOP ==================
running = True
buttons = {}

while running:
    clock.tick(60)
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # INPUT NAMA
        if state == "NAME" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and player_name:
                state = "LEVEL"
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                player_name += event.unicode

        # PILIH WARNA
        if state == "PLAY" and event.type == pygame.MOUSEBUTTONDOWN:
            for name, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    user_input.append(name)
                    selected_color = name

                    if len(user_input) == len(sequence):
                        reaction_time = time.time() - start_time
                        if user_input == sequence:
                            message = "BENAR"
                            save_data("BENAR")

                            fireworks = []
                            for _ in range(60):
                                fireworks.append(
                                    FireworkParticle(WIDTH // 2, HEIGHT // 2)
                                )
                            show_fireworks = True
                        else:
                            message = "SALAH"
                            save_data("SALAH")
                            show_fireworks = False

                        result_time = time.time()
                        state = "RESULT"

    # ================== STATE UI ==================
    if state == "MENU":
        draw_text("GAME MEMORI WARNA", 150, font_title)
        draw_text("Latih daya ingat dengan warna", 220, font_small)
        btn = pygame.Rect(350, 350, 200, 70)
        draw_button(btn, "MULAI")

        if pygame.mouse.get_pressed()[0] and btn.collidepoint(pygame.mouse.get_pos()):
            pygame.time.delay(200)
            state = "NAME"

    elif state == "NAME":
        draw_text("Masukkan Nama", 200, font_big)
        pygame.draw.rect(screen, WHITE, (250, 260, 400, 60), border_radius=15)
        draw_text(player_name + "|", 290, font_small)

    elif state == "LEVEL":
        draw_text("Pilih Level", 150, font_big)

        button_width = 180
        button_height = 70
        gap = 40
        start_x = (WIDTH - (3 * button_width + 2 * gap)) // 2
        y = 350

        btn_easy = pygame.Rect(start_x, y, button_width, button_height)
        btn_medium = pygame.Rect(start_x + button_width + gap, y, button_width, button_height)
        btn_hard = pygame.Rect(start_x + 2 * (button_width + gap), y, button_width, button_height)

        draw_button(btn_easy, "MUDAH")
        draw_button(btn_medium, "SEDANG")
        draw_button(btn_hard, "SULIT")

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if btn_easy.collidepoint(pos):
                level_name, base_length = "Mudah", 3
            elif btn_medium.collidepoint(pos):
                level_name, base_length = "Sedang", 4
            elif btn_hard.collidepoint(pos):
                level_name, base_length = "Sulit", 5

            sequence = generate_sequence(base_length)
            user_input = []
            selected_color = ""
            start_time = time.time()
            state = "SHOW"
            pygame.time.delay(200)


    elif state == "SHOW":
        draw_text(f"Level: {level_name}", 120, font_big)
        draw_text("Ingat urutan warna", 220, font_small)
        draw_text(" - ".join(sequence), 280, font_big)
        if time.time() - start_time > 3:
            start_time = time.time()
            state = "PLAY"

    elif state == "PLAY":
        draw_text(f"Nama: {player_name}", 40, font_small)
        draw_text(f"Level: {level_name}", 70, font_small)
        buttons = draw_color_buttons()
        if selected_color:
            draw_text(f"Dipilih: {selected_color}", 260, font_small)

    elif state == "RESULT":
        draw_text(message, HEIGHT // 2, font_big)
        if show_fireworks:
            for p in fireworks[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    fireworks.remove(p)
        if time.time() - result_time > 2:
            show_fireworks = False
            state = "MENU"
            player_name = ""

    pygame.display.update()

pygame.quit()
sys.exit()
