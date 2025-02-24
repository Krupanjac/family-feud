import pygame, sys, sqlite3, os, math, json, random
from pygame.locals import KEYDOWN, K_ESCAPE, K_x, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

# ----------------- Constants -----------------
DEFAULT_SETTINGS = {
    "screen_width": 1200,
    "screen_height": 800,
    "fullscreen": False,
    "volume": 100
}

WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)
GRAY     = (200, 200, 200)
RED      = (255, 0, 0)
BLUE     = (0, 0, 255)
GOLD     = (212, 175, 55)
DARK_RED = (139, 0, 0)
YELLOW   = (255, 215, 0)

REGULAR  = 36
QUESTION = 50

ZOOM_SPEED = 0.0007  # for background effect

# ----------------- Helper Classes -----------------
class ConfettiParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(5, 10)
        self.color = random.choice([RED, BLUE, GOLD, YELLOW, WHITE])
        self.velocity = [random.uniform(-2, 2), random.uniform(2, 5)]
        self.gravity = 0.1

    def update(self):
        self.velocity[1] += self.gravity
        self.x += self.velocity[0]
        self.y += self.velocity[1]

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.size, self.size))

class BackgroundEffect:
    def __init__(self, base_bg):
        self.base_bg = base_bg
        self.original_bg = base_bg.copy() if base_bg else None
        self.zoom_phase = 0

    def update(self, dt):
        self.zoom_phase = (self.zoom_phase + ZOOM_SPEED * dt) % math.pi

    def get_transformed_bg(self, screen_width, screen_height):
        if not self.original_bg:
            return None
        img_w = self.original_bg.get_width()
        img_h = self.original_bg.get_height()
        # Compute a scale factor so the image covers the entire screen.
        base_scale = max(screen_width / img_w, screen_height / img_h)
        zoom_scale = 1.0 + 0.1 * math.sin(self.zoom_phase)
        final_scale = base_scale * zoom_scale
        new_w = int(img_w * final_scale)
        new_h = int(img_h * final_scale)
        scaled_bg = pygame.transform.smoothscale(self.original_bg, (new_w, new_h))
        return scaled_bg

# ----------------- Main Game Class -----------------
class FamilyFeudGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.settings = self.load_settings()
        self.screen_width = self.settings["screen_width"]
        self.screen_height = self.settings["screen_height"]
        flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags)
        pygame.display.set_caption("Породични Дуел! РГДЕВ - ЕТФ")
        favicon_path = "assets/favicon.png"
        if os.path.exists(favicon_path):
            icon = pygame.image.load(favicon_path)
            pygame.display.set_icon(icon)
        self.font_regular = pygame.font.SysFont(None, REGULAR)
        self.font_question = pygame.font.SysFont(None, QUESTION)
        self.clock = pygame.time.Clock()
        self.correct_sound = self.load_sound("assets/correct.wav")
        self.wrong_sound = self.load_sound("assets/wrong.wav")
        if self.correct_sound:
            self.correct_sound.set_volume(self.settings.get("volume", 100) / 100)
        if self.wrong_sound:
            self.wrong_sound.set_volume(0.4 * self.settings.get("volume", 100) / 100)
        self.conn = self.init_db()
        self.team1_name, self.team2_name = self.load_team_names()
        self.background = self.load_background()
        self.bg_effect = BackgroundEffect(self.background)
        self.total_team1 = 0
        self.total_team2 = 0
        self.round_results = []

    # Settings I/O
    def load_settings(self):
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=4)

    # Resource loading
    def load_background(self):
        bg_filename = "assets/background.jpg"
        if os.path.exists(bg_filename):
            # Load the full-res image and downscale once for performance.
            bg = pygame.image.load(bg_filename).convert()
            current_width, current_height = self.screen.get_size()
            base_scale = max(current_width / bg.get_width(), current_height / bg.get_height())
            scale_factor = base_scale * 1.1  # add margin for zoom
            new_w = int(bg.get_width() * scale_factor)
            new_h = int(bg.get_height() * scale_factor)
            bg = pygame.transform.smoothscale(bg, (new_w, new_h))
            return bg
        else:
            bg = pygame.Surface((self.screen_width, self.screen_height))
            bg.fill(DARK_RED)
            pygame.draw.circle(bg, YELLOW, (self.screen_width//2, self.screen_height//2), 100)
            return bg

    def load_sound(self, filename):
        return pygame.mixer.Sound(filename) if os.path.exists(filename) else None

    def init_db(self):
        db_filename = "family_feud.db"
        if os.path.exists(db_filename):
            os.remove(db_filename)
        conn = sqlite3.connect(db_filename)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rounds (
                round_number INTEGER PRIMARY KEY,
                team1_points INTEGER,
                team2_points INTEGER
            )
        """)
        conn.commit()
        return conn

    def save_round_result(self, round_number, team1_points, team2_points):
        self.conn.execute("INSERT INTO rounds (round_number, team1_points, team2_points) VALUES (?, ?, ?)",
                          (round_number, team1_points, team2_points))
        self.conn.commit()

    def load_team_names(self):
        teams_file = "teams.txt"
        if os.path.exists(teams_file):
            with open(teams_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if len(lines) >= 2:
                    return lines[0], lines[1]
        return "Тим1", "Тим2"

    # Drawing helpers
    def draw_footer(self):
        footer_font = pygame.font.SysFont(None, 20, italic=True)
        footer_text = footer_font.render("РГ за истраживачко-развојне делатности, ЕТФ, 2025 ©", True, GOLD)
        self.screen.blit(footer_text, (self.screen_width - footer_text.get_width() - 10,
                                       self.screen_height - footer_text.get_height() - 10))

    def draw_background(self):
        current_width, current_height = self.screen.get_size()
        if self.bg_effect.original_bg:
            scaled_bg = self.bg_effect.get_transformed_bg(current_width, current_height)
            rect = scaled_bg.get_rect(center=(current_width // 2, current_height // 2))
            self.screen.blit(scaled_bg, rect)

    @staticmethod
    def screen_shake_offset(intensity=10):
        return random.randint(-intensity, intensity), random.randint(-intensity, intensity)

    def fade_transition(self, fade_in=True, duration=500):
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        current_size = self.screen.get_size()
        while True:
            elapsed = pygame.time.get_ticks() - start_time
            if elapsed > duration:
                break
            self.draw_background()
            overlay = pygame.Surface(current_size)
            overlay.fill(DARK_RED)
            alpha = int((elapsed / duration) * 255) if fade_in else 255 - int((elapsed / duration) * 255)
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            clock.tick(60)

    def show_confetti(self, duration=3000):
        if self.total_team1 == self.total_team2:
            winner = "Нерешено!"
        else:
            winner = f"Победник: {self.team1_name}" if self.total_team1 > self.total_team2 else f"Победник: {self.team2_name}"
        particles = [ConfettiParticle(random.randint(0, self.screen_width), 0) for _ in range(150)]
        start_time = pygame.time.get_ticks()
        final_font = pygame.font.SysFont(None, 60)
        while pygame.time.get_ticks() - start_time < duration:
            self.draw_background()
            for p in particles:
                p.update()
                p.draw(self.screen)
            final_msg = f"Коначни резултат - {self.team1_name}: {self.total_team1} | {self.team2_name}: {self.total_team2}"
            final_surf = final_font.render(final_msg, True, WHITE)
            winner_surf = final_font.render(winner, True, BLUE)
            self.screen.blit(final_surf, ((self.screen_width - final_surf.get_width()) // 2, self.screen_height // 2 - 50))
            self.screen.blit(winner_surf, ((self.screen_width - winner_surf.get_width()) // 2, self.screen_height // 2 + 20))
            self.draw_footer()
            pygame.display.flip()
            self.clock.tick(60)

    def show_round_over_popup(self, round_results):
        popup_w, popup_h = self.screen_width // 2, self.screen_height // 2
        popup = pygame.Surface((popup_w, popup_h))
        popup.fill((30, 30, 30))
        popup.set_alpha(240)
        header_font = pygame.font.SysFont(None, int(REGULAR * 1.2))
        header_surf = header_font.render("Рунда Завршена", True, GOLD)
        popup.blit(header_surf, header_surf.get_rect(center=(popup_w // 2, 30)))
        scoreboard = f"Скор: {self.total_team1}:{self.total_team2}"
        popup.blit(self.font_regular.render(scoreboard, True, WHITE),
                   (popup_w // 2 - self.font_regular.size(scoreboard)[0] // 2, 60))
        popup.blit(self.font_regular.render("Рунде:", True, WHITE),
                   (popup_w // 2 - self.font_regular.size("Рунде:")[0] // 2, 100))
        y_offset = 130
        for result in round_results:
            text_surf = self.font_regular.render(result, True, WHITE)
            popup.blit(text_surf, (popup_w // 2 - text_surf.get_width() // 2, y_offset))
            y_offset += text_surf.get_height() + 5
        pygame.draw.rect(popup, GOLD, popup.get_rect(), 3)
        for scale in range(50, 101, 5):
            scaled = pygame.transform.smoothscale(popup, (popup_w * scale // 100, popup_h * scale // 100))
            rect = scaled.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.draw_background()
            self.screen.blit(scaled, rect)
            pygame.display.flip()
            pygame.time.delay(30)
        self.screen.blit(popup, popup.get_rect(center=(self.screen_width // 2, self.screen_height // 2)))
        pygame.display.flip()
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 5000:
            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN) and (event.type != KEYDOWN or event.key == K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type in (KEYDOWN, MOUSEBUTTONDOWN):
                    return
            pygame.time.delay(100)

    def show_wrong_feedback(self):
        if self.wrong_sound:
            self.wrong_sound.play()
        bg_copy = self.screen.copy()
        start_time = pygame.time.get_ticks()
        duration = 1250
        intensity = 10
        big_font = pygame.font.SysFont(None, 300)
        orig_x = big_font.render("X", True, RED).convert_alpha()
        orig_x.set_colorkey((0, 0, 0))
        while pygame.time.get_ticks() - start_time < duration:
            elapsed = pygame.time.get_ticks() - start_time
            alpha = max(255 - int(255 * (elapsed / duration)), 0)
            scale = 1.0 + 0.5 * (elapsed / duration)
            new_size = (int(orig_x.get_width() * scale), int(orig_x.get_height() * scale))
            scaled_x = pygame.transform.smoothscale(orig_x, new_size)
            scaled_x.set_alpha(alpha)
            offset = self.screen_shake_offset(intensity)
            self.screen.blit(bg_copy, (0, 0))
            rect = scaled_x.get_rect(center=(self.screen_width // 2 + offset[0], self.screen_height // 2 + offset[1]))
            self.screen.blit(scaled_x, rect)
            pygame.display.flip()
            self.clock.tick(60)

    def draw_board(self, question, answers, strikes, state, active_team):
        self.screen.fill(BLACK)
        self.draw_background()

        # Draw current score.
        score_text = f"Резултат - {self.team1_name}: {self.total_team1} | {self.team2_name}: {self.total_team2}"
        self.screen.blit(self.font_regular.render(score_text, True, WHITE),
                         (self.screen_width - self.font_regular.size(score_text)[0] - 20, 20))

        # Draw active team indicator.
        active_text = f"Активни тим: {self.team1_name if active_team == 1 else self.team2_name}"
        color = RED if active_team == 1 else BLUE
        self.screen.blit(self.font_regular.render(active_text, True, color),
                         (self.screen_width - self.font_regular.size(active_text)[0] - 20, 60))

        # Draw the question.
        question_surf = self.font_question.render(question, True, BLACK)
        question_y = (self.screen_height - question_surf.get_height() - len(answers) * 60) // 2
        self.screen.blit(question_surf, ((self.screen_width - question_surf.get_width()) // 2, question_y))

        rects = []
        current_time = pygame.time.get_ticks() / 500  # used in pulsing border animation
        answer_y = question_y + question_surf.get_height() + 20

        if len(answers) > 4:
            rows = math.ceil(len(answers) / 2)
            col_w = (self.screen_width - 150) // 2
            left_x, right_x = 50, 50 + col_w + 50
            for row in range(rows):
                y = answer_y + row * 60
                for col, idx in enumerate([row * 2, row * 2 + 1]):
                    if idx < len(answers):
                        x = left_x if col == 0 else right_x
                        rect = pygame.Rect(x, y, col_w, 50)
                        # Draw drop shadow
                        shadow_rect = rect.move(3, 3)
                        pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=8)
                        # Draw rounded answer box
                        pygame.draw.rect(self.screen, GRAY, rect, border_radius=8)
                        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
                        # Draw pulsing border if revealed
                        if answers[idx]["revealed"]:
                            pulse = int(5 * abs(math.sin(current_time)))
                            pygame.draw.rect(self.screen, YELLOW, rect.inflate(pulse, pulse), 4, border_radius=8)
                            text = f"{idx+1}. {answers[idx]['answer']} - {answers[idx]['points']}"
                        else:
                            text = f"{idx+1}."
                        text_surf = self.font_regular.render(text, True, BLACK)
                        self.screen.blit(text_surf,
                                         (rect.x + 10, rect.y + (50 - self.font_regular.get_height()) // 2))
                        rects.append(rect)
        else:
            for i, ans in enumerate(answers):
                rect = pygame.Rect(50, answer_y + i * 60, self.screen_width - 100, 50)
                # Draw drop shadow
                shadow_rect = rect.move(3, 3)
                pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=8)
                # Draw rounded answer box
                pygame.draw.rect(self.screen, GRAY, rect, border_radius=8)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
                # Draw pulsing border if revealed
                if ans["revealed"]:
                    pulse = int(5 * abs(math.sin(current_time)))
                    pygame.draw.rect(self.screen, YELLOW, rect.inflate(pulse, pulse), 4, border_radius=8)
                    text = f"{i+1}. {ans['answer']} - {ans['points']}"
                else:
                    text = f"{i+1}."
                text_surf = self.font_regular.render(text, True, BLACK)
                self.screen.blit(text_surf,
                                 (rect.x + 10, rect.y + (50 - self.font_regular.get_height()) // 2))
                rects.append(rect)

        # Draw strikes indicator.
        strikes_text = f"Погрешних: {strikes}"
        self.screen.blit(self.font_regular.render(strikes_text, True, RED), (50, self.screen_height - 50))

        # In case of opponent state, show additional message.
        if state == "opponent":
            opp_text = "Шанса противника!"
            self.screen.blit(self.font_regular.render(opp_text, True, BLUE), (50, self.screen_height - 100))

        self.draw_footer()
        pygame.display.flip()
        return rects

    def settings_menu(self):
        # Save original settings in case of cancelation.
        orig_settings = {
            "screen_width": self.settings.get("screen_width", 1200),
            "screen_height": self.settings.get("screen_height", 800),
            "volume": self.settings.get("volume", 100),
            "fullscreen": self.settings.get("fullscreen", False)
        }
        # Modal dimensions
        modal_w, modal_h = 600, 400
        current_width, current_height = self.screen.get_size()
        modal_x = (current_width - modal_w) // 2
        modal_y = (current_height - modal_h) // 2

        # Initialize local values (as strings for text input)
        manual_width = str(self.settings.get("screen_width", 1200))
        manual_height = str(self.settings.get("screen_height", 800))
        volume = self.settings.get("volume", 100)
        fullscreen = self.settings.get("fullscreen", False)

        # Flags for input boxes
        width_active = False
        height_active = False

        font = pygame.font.SysFont(None, 32)
        canceled = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == KEYDOWN:
                    # If an input box is active, update the corresponding string.
                    if width_active:
                        if event.key == pygame.K_RETURN:
                            width_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            manual_width = manual_width[:-1]
                        elif event.unicode.isdigit():
                            manual_width += event.unicode
                    elif height_active:
                        if event.key == pygame.K_RETURN:
                            height_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            manual_height = manual_height[:-1]
                        elif event.unicode.isdigit():
                            manual_height += event.unicode
                    elif event.key == K_ESCAPE:
                        # Cancel modifications.
                        canceled = True
                        running = False
                elif event.type == MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Translate mouse coordinates relative to modal
                    rel_x = mx - modal_x
                    rel_y = my - modal_y
                    width_box = pygame.Rect(200, 20, 150, 30)
                    height_box = pygame.Rect(200, 70, 150, 30)
                    volume_slider = pygame.Rect(200, 120, 300, 20)
                    checkbox = pygame.Rect(200, 170, 30, 30)
                    if width_box.collidepoint(rel_x, rel_y):
                        width_active = True
                        height_active = False
                    elif height_box.collidepoint(rel_x, rel_y):
                        height_active = True
                        width_active = False
                    elif volume_slider.collidepoint(rel_x, rel_y):
                        ratio = (rel_x - volume_slider.x) / volume_slider.width
                        new_volume = int(min(max(ratio, 0), 1) * 100)
                        if new_volume != volume:
                            volume = new_volume
                            if self.wrong_sound:
                                self.wrong_sound.set_volume(0.4 * (volume / 100))
                                self.wrong_sound.play()
                    elif checkbox.collidepoint(rel_x, rel_y):
                        fullscreen = not fullscreen
                    else:
                        width_active = False
                        height_active = False
                    # Check if "Save" button is clicked
                    save_rect = pygame.Rect(modal_w//2 - 50, modal_h - 60, 100, 40)
                    if save_rect.collidepoint(rel_x, rel_y):
                        running = False
                elif event.type == MOUSEMOTION and event.buttons[0]:
                    mx, my = event.pos
                    rel_x = mx - modal_x
                    rel_y = my - modal_y
                    volume_slider = pygame.Rect(200, 120, 300, 20)
                    if volume_slider.collidepoint(rel_x, rel_y):
                        ratio = (rel_x - volume_slider.x) / volume_slider.width
                        new_volume = int(min(max(ratio, 0), 1) * 100)
                        if new_volume != volume:
                            volume = new_volume
                            if self.wrong_sound:
                                self.wrong_sound.set_volume(0.4 * (volume / 100))
                                self.wrong_sound.play()

            # Draw modal
            modal = pygame.Surface((modal_w, modal_h))
            modal.fill((50, 50, 50))
            pygame.draw.rect(modal, WHITE, modal.get_rect(), 2)

            # "Screen Width" label and input field
            modal.blit(font.render("Screen Width:", True, WHITE), (20, 20))
            pygame.draw.rect(modal, WHITE, (200, 20, 150, 30), 2)
            text_width = font.render(manual_width, True, WHITE)
            modal.blit(text_width, (205, 25))
            if width_active and (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = 205 + text_width.get_width() + 2
                pygame.draw.line(modal, WHITE, (cursor_x, 25), (cursor_x, 25 + text_width.get_height()), 2)

            # "Screen Height" label and input field
            modal.blit(font.render("Screen Height:", True, WHITE), (20, 70))
            pygame.draw.rect(modal, WHITE, (200, 70, 150, 30), 2)
            text_height = font.render(manual_height, True, WHITE)
            modal.blit(text_height, (205, 75))
            if height_active and (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = 205 + text_height.get_width() + 2
                pygame.draw.line(modal, WHITE, (cursor_x, 75), (cursor_x, 75 + text_height.get_height()), 2)

            # Volume slider
            modal.blit(font.render("Volume:", True, WHITE), (20, 120))
            pygame.draw.rect(modal, GRAY, (200, 120, 300, 20))
            vol_ratio = volume / 100
            knob_x = 200 + int(vol_ratio * 300) - 5
            pygame.draw.rect(modal, WHITE, (knob_x, 115, 10, 30))

            # Fullscreen checkbox
            modal.blit(font.render("Fullscreen:", True, WHITE), (20, 170))
            pygame.draw.rect(modal, WHITE, (200, 170, 30, 30), 2)
            if fullscreen:
                pygame.draw.rect(modal, WHITE, (203, 173, 24, 24))

            # Save button
            save_rect = pygame.Rect(modal_w//2 - 50, modal_h - 60, 100, 30)
            pygame.draw.rect(modal, GRAY, save_rect)
            modal.blit(font.render("Сачувај", True, BLACK), (save_rect.x + 5, save_rect.y + 5))

            # Instructions
            modal.blit(font.render("Press ESC to cancel", True, WHITE), (modal_w//2 - 100, modal_h - 25))

            # Blit modal centered on screen (overlaying current background)
            self.screen.fill(BLACK)
            self.draw_background()
            self.screen.blit(modal, (modal_x, modal_y))
            pygame.display.flip()
            self.clock.tick(60)

        # If canceled, do not change settings.
        if canceled:
            return orig_settings

        try:
            new_width = int(manual_width)
        except ValueError:
            new_width = self.settings.get("screen_width", 1200)
        try:
            new_height = int(manual_height)
        except ValueError:
            new_height = self.settings.get("screen_height", 800)
        self.settings["screen_width"] = new_width
        self.settings["screen_height"] = new_height
        self.settings["volume"] = volume
        self.settings["fullscreen"] = fullscreen
        self.save_settings()
        return self.settings

    def choose_team(self, total_team1, total_team2):
        selecting = True
        current_x = -300
        target_x = 50
        last_time = pygame.time.get_ticks()
        while selecting:
            dt = pygame.time.get_ticks() - last_time
            last_time = pygame.time.get_ticks()
            current_x = min(target_x, current_x + dt * 0.5)
            self.bg_effect.update(dt)
            self.screen.fill(BLACK)
            self.draw_background()
            prompt1 = "Који тим игра у овој рунди?"
            prompt2 = f"Притисните 1 за {self.team1_name} или 2 за {self.team2_name}"
            self.screen.blit(self.font_regular.render(prompt1, True, WHITE), (current_x, self.screen_height // 2 - 60))
            self.screen.blit(self.font_regular.render(prompt2, True, WHITE), (current_x, self.screen_height // 2))
            scoreboard = f"Резултат уживо - {self.team1_name}: {total_team1} | {self.team2_name}: {total_team2}"
            self.screen.blit(self.font_regular.render(scoreboard, True, WHITE), (self.screen_width // 3, self.screen_height // 80))
            hint = self.font_regular.render("Притисни П да отвориш опције", True, WHITE)
            self.screen.blit(hint, (50, self.screen_height - 50))
            self.draw_footer()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_p:
                        self.settings = self.settings_menu()
                        flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
                        self.screen = pygame.display.set_mode((self.settings["screen_width"], self.settings["screen_height"]), flags)
                        self.screen_width = self.settings["screen_width"]
                        self.screen_height = self.settings["screen_height"]
                        if self.wrong_sound:
                            self.wrong_sound.set_volume(0.4 * (self.settings.get("volume", 100) / 100))
                        if self.correct_sound:
                            self.correct_sound.set_volume(self.settings.get("volume", 100) / 100)
                        self.font_regular = pygame.font.SysFont(None, REGULAR)
                        continue
                    elif event.unicode == '1':
                        if self.correct_sound:
                            self.correct_sound.play()
                        self.fade_transition(fade_in=False, duration=500)
                        return 1
                    elif event.unicode == '2':
                        if self.correct_sound:
                            self.correct_sound.play()
                        self.fade_transition(fade_in=False, duration=500)
                        return 2
            self.clock.tick(60)
        return 1

    def run(self):
        for round_num in range(1, 6):
            active_team = self.choose_team(self.total_team1, self.total_team2)
            team1_round, team2_round = 0, 0
            round_file = f"questions/round{round_num}.txt"
            if not os.path.exists(round_file):
                print(f"Фајл {round_file} није пронађен.")
                continue
            with open(round_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if not lines:
                continue
            question = lines[0]
            answers = []
            for line in lines[1:]:
                parts = line.split(',')
                if len(parts) == 2:
                    try:
                        points = int(parts[1].strip())
                    except ValueError:
                        points = 0
                    answers.append({"answer": parts[0].strip(), "points": points, "revealed": False})
            strikes = 0
            state = "active"
            last_time = pygame.time.get_ticks()
            while True:
                dt = pygame.time.get_ticks() - last_time
                last_time = pygame.time.get_ticks()
                self.bg_effect.update(dt)
                rects = self.draw_board(question, answers, strikes, state, active_team)
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit(); sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == pygame.K_p:
                            self.settings = self.settings_menu()
                            flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
                            self.screen = pygame.display.set_mode((self.settings["screen_width"], self.settings["screen_height"]), flags)
                            self.screen_width = self.settings["screen_width"]
                            self.screen_height = self.settings["screen_height"]
                            if self.wrong_sound:
                                self.wrong_sound.set_volume(0.4 * (self.settings.get("volume", 100) / 100))
                            if self.correct_sound:
                                self.correct_sound.set_volume(self.settings.get("volume", 100) / 100)
                            self.font_regular = pygame.font.SysFont(None, REGULAR)
                            continue
                        elif state == "active":
                            if event.unicode.isdigit():
                                idx = int(event.unicode) - 1
                                if 0 <= idx < len(answers) and not answers[idx]["revealed"]:
                                    answers[idx]["revealed"] = True
                                    if self.correct_sound:
                                        self.correct_sound.play()
                                    if active_team == 1:
                                        team1_round += answers[idx]["points"]
                                    else:
                                        team2_round += answers[idx]["points"]
                            elif event.key == pygame.K_x:
                                self.show_wrong_feedback()
                                strikes += 1
                                if strikes >= 3:
                                    state = "opponent" if not all(a["revealed"] for a in answers) else "round_over"
                        elif state == "opponent":
                            if event.unicode.isdigit():
                                idx = int(event.unicode) - 1
                                if 0 <= idx < len(answers) and not answers[idx]["revealed"]:
                                    answers[idx]["revealed"] = True
                                    if self.correct_sound:
                                        self.correct_sound.play()
                                    if active_team == 1:
                                        team2_round = team1_round + answers[idx]["points"]
                                        team1_round = 0
                                    else:
                                        team1_round = team2_round + answers[idx]["points"]
                                        team2_round = 0
                                    state = "round_over"
                            elif event.key == pygame.K_x:
                                self.show_wrong_feedback()
                                state = "round_over"
                    elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                        pos = pygame.mouse.get_pos()
                        for i, rect in enumerate(rects):
                            if rect.collidepoint(pos) and not answers[i]["revealed"]:
                                answers[i]["revealed"] = True
                                if self.correct_sound:
                                    self.correct_sound.play()
                                if state == "active":
                                    if active_team == 1:
                                        team1_round += answers[i]["points"]
                                    else:
                                        team2_round += answers[i]["points"]
                                elif state == "opponent":
                                    if active_team == 1:
                                        team2_round = team1_round + answers[i]["points"]
                                        team1_round = 0
                                    else:
                                        team1_round = team2_round + answers[i]["points"]
                                        team2_round = 0
                                    state = "round_over"
                if state == "active" and all(a["revealed"] for a in answers):
                    state = "round_over"
                if state == "round_over":
                    self.draw_board(question, answers, strikes, state, active_team)
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    if active_team == 1:
                        self.total_team1 += team1_round
                        self.total_team2 += team2_round
                    else:
                        self.total_team2 += team2_round
                        self.total_team1 += team1_round
                    self.save_round_result(round_num, self.total_team1, self.total_team2)
                    self.round_results.append(f"Рунда {round_num}: {team1_round}:{team2_round}")
                    self.fade_transition(fade_in=False, duration=500)
                    self.show_round_over_popup(self.round_results)
                    self.fade_transition(fade_in=True, duration=500)
                    break
                self.clock.tick(60)
        self.draw_background()
        self.show_confetti(duration=3000)
        pygame.time.wait(5000)
        self.conn.close()
        # Instead of quitting, return to allow game restart.
        return

if __name__ == "__main__":
    # Restart the game when it completes.
    while True:
        FamilyFeudGame().run()
