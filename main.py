import pygame, sys, sqlite3, os, math, json, random, cv2
from pygame.locals import KEYDOWN, K_ESCAPE, K_x, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

def resource_path(relative_path):
    """Get absolute path to resource, works for development and for PyInstaller onefile."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ----------------- Constants -----------------
DEFAULT_SETTINGS = {
    "screen_width": 1200,
    "screen_height": 800,
    "fullscreen": False,
    "volume": 100,
    "music_volume": 100
}

WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)
GRAY     = (200, 200, 200)
RED      = (255, 0, 0)
BLUE     = (0, 0, 255)
GOLD     = (212, 175, 55)
DARK_RED = (139, 0, 0)
YELLOW   = (255, 215, 0)

# Font sizes - centralized for easy modification
REGULAR_SIZE   = 28
QUESTION_SIZE  = 40
FOOTER_SIZE    = 20
HEADER_SIZE    = int(REGULAR_SIZE * 1.2)
FINAL_SIZE     = 60
BIG_SIZE       = 300
SETTINGS_SIZE  = 21

BOARD_VERTICAL_OFFSET = 100  # Shift the question/answers board downward

# Font paths - search in these locations with these filenames
FONT_PATHS = [
    "assets/fonts/OpenSans-Regular.ttf",
    "assets/fonts/Roboto-Regular.ttf"
]

# Bold font paths
BOLD_FONT_PATHS = [
    "assets/fonts/OpenSans-Bold.ttf",
    "assets/fonts/Roboto-Bold.ttf"
]

# ----------------- Helper Functions -----------------
def load_font(font_paths, size, fallback_name=None):
    """Try to load fonts from the given paths, with fallback to system font."""
    for path in font_paths:
        try:
            full_path = resource_path(path)
            if os.path.exists(full_path):
                return pygame.font.Font(full_path, size)
        except Exception as e:
            print(f"Could not load font {path}: {e}")
    
    # If we get here, none of the custom fonts worked
    return pygame.font.SysFont(fallback_name, size)

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

class VideoBackground:
    def __init__(self, video_path, fallback_image_path):
        # Load the fallback image first
        self.fallback_image = None
        if os.path.exists(fallback_image_path):
            self.fallback_image = pygame.image.load(fallback_image_path).convert()
        
        # Attempt to load the video
        self.video_frames = []
        self.current_frame_index = 0
        self.frame_delay = 30  # Default ~30 FPS
        self.last_frame_time = 0
        self.playing_forward = True  # Track direction of playback
        
        if os.path.exists(video_path):
            try:
                import cv2
                self.cap = cv2.VideoCapture(video_path)
                if not self.cap.isOpened():
                    print(f"Failed to open video file: {video_path}")
                else:
                    self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                    if self.fps > 0:
                        self.frame_delay = int(1000 / self.fps)
                    
                    # Pre-load all frames to allow for reverse playback
                    max_preload_frames = 120  # Approximately 4 seconds at 30fps
                    for _ in range(max_preload_frames):
                        ret, frame = self.cap.read()
                        if not ret:
                            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret, frame = self.cap.read()
                            if not ret:
                                break
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pygame_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                        self.video_frames.append(pygame_frame)
            except (ImportError, Exception) as e:
                print(f"Error loading video: {e}")
        
        self.is_video_loaded = len(self.video_frames) > 0

    def update(self, dt):
        if not self.is_video_loaded or not self.video_frames:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time >= self.frame_delay:
            self.last_frame_time = current_time
            
            # Update frame index based on direction (forward or reverse)
            if self.playing_forward:
                self.current_frame_index += 1
                # If we reach the end, reverse direction
                if self.current_frame_index >= len(self.video_frames) - 1:
                    self.playing_forward = False
            else:
                self.current_frame_index -= 1
                # If we reach the beginning, reverse direction
                if self.current_frame_index <= 0:
                    self.playing_forward = True

    def get_frame(self, screen_width, screen_height):
        if self.is_video_loaded and self.video_frames:
            current_frame = self.video_frames[self.current_frame_index]
            frame_w, frame_h = current_frame.get_size()
            scale = max(screen_width / frame_w, screen_height / frame_h)
            new_w = int(frame_w * scale)
            new_h = int(frame_h * scale)
            return pygame.transform.scale(current_frame, (new_w, new_h))
        elif self.fallback_image:
            img_w = self.fallback_image.get_width()
            img_h = self.fallback_image.get_height()
            scale = max(screen_width / img_w, screen_height / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            return pygame.transform.scale(self.fallback_image, (new_w, new_h))
        else:
            surface = pygame.Surface((screen_width, screen_height))
            surface.fill(DARK_RED)
            pygame.draw.circle(surface, YELLOW, (screen_width // 2, screen_height // 2), 100)
            return surface

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
        
        favicon_path = resource_path("assets/favicon.png")
        if os.path.exists(favicon_path):
            icon = pygame.image.load(favicon_path)
            pygame.display.set_icon(icon)
        
        self.clock = pygame.time.Clock()
        # Display a simple initialization screen
        self.show_loading_screen()
        # Load assets (fonts, video, sounds, music) with a loading bar
        self.load_assets()
        
        self.conn = self.init_db()
        self.team1_name, self.team2_name = self.load_team_names()
        
        self.total_team1 = 0
        self.total_team2 = 0
        self.round_results = []
        self.last_glaze_time = pygame.time.get_ticks()
        self.glaze_effect_duration = 700  # milliseconds
        self.active_glaze_index = None
        self.glaze_start_time = None
        self.last_glazed_index = None

    def show_loading_screen(self):
        # Display an initial message while the assets are about to load.
        self.screen.fill(BLACK)
        basic_font = pygame.font.SysFont("Roboto", 30)
        loading_text = basic_font.render("Учитавање...", True, WHITE)
    def draw_loading_bar(self, progress):
        # Try to load the background image
        loader_path = resource_path("assets/loader.png")
        if os.path.exists(loader_path):
            try:
                loader_bg = pygame.image.load(loader_path)
                self.screen.blit(loader_bg, (-25, 100))
            except Exception as e:
                # If loading fails, fall back to black background
                print(f"Could not load loader.png: {e}")
                self.screen.fill(BLACK)
        else:
            # If the image doesn't exist, use black background
            self.screen.fill(BLACK)
        # Define dimensions for the loading bar
        bar_width = self.screen_width // 2
        bar_height = 30
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = (self.screen_height - bar_height) - 200
        
        # Colors for the modern look
        bg_color = (30, 30, 30)         # Dark grey background for the bar
        fill_color = DARK_RED               # The main fill color (blue)
        shadow_color = (20, 20, 20)       # A dark shade for the shadow
        
        # Draw a subtle drop shadow (offset by a few pixels)
        shadow_offset = 4
        shadow_rect = pygame.Rect(
            bar_x + shadow_offset, 
            bar_y + shadow_offset, 
            bar_width, 
            bar_height
        )
        pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=15)
        
        # Draw the background of the loading bar with rounded corners
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, bg_color, bar_rect, border_radius=15)
        
        # Calculate fill width based on progress and draw the progress fill
        fill_width = int(progress * bar_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=15)
            
            # Add a glossy highlight on the top half to simulate shine
            highlight_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height // 2)
            highlight_surface = pygame.Surface((fill_width, bar_height // 2), pygame.SRCALPHA)
            highlight_surface.fill((255, 255, 255, 50))  # Semi-transparent white overlay
            self.screen.blit(highlight_surface, (bar_x, bar_y))
        
        # Render the loading text above the bar
        font = pygame.font.SysFont("Roboto", 24)
        loading_text = font.render("Учитавам...", True, WHITE)
        text_rect = loading_text.get_rect(center=(self.screen_width // 2, bar_y - 20))
        self.screen.blit(loading_text, text_rect)
        
        # Update the display
        pygame.display.flip()


    def load_assets(self):
        total_steps = 4
        current_step = 0

        # Step 1: Load fonts
        self.font_regular = load_font(FONT_PATHS, REGULAR_SIZE, "Roboto")
        self.font_question = load_font(BOLD_FONT_PATHS, QUESTION_SIZE, "Roboto")
        self.font_footer = load_font(FONT_PATHS, FOOTER_SIZE, "Roboto")
        current_step += 1
        self.draw_loading_bar(current_step / total_steps)
        pygame.time.wait(200)

        # Step 2: Load video background
        video_path = resource_path("assets/background.mp4")
        fallback_image_path = resource_path("assets/background.jpg")
        self.video_bg = VideoBackground(video_path, fallback_image_path)
        current_step += 1
        self.draw_loading_bar(current_step / total_steps)
        pygame.time.wait(200)

        # Step 3: Load sounds
        self.correct_sound = self.load_sound("assets/correct.wav")
        self.wrong_sound = self.load_sound("assets/wrong.wav")
        if self.correct_sound:
            self.correct_sound.set_volume(self.settings.get("volume", 100) / 100)
        if self.wrong_sound:
            self.wrong_sound.set_volume(0.4 * self.settings.get("volume", 100) / 100)
        current_step += 1
        self.draw_loading_bar(current_step / total_steps)
        pygame.time.wait(200)

        # Step 4: Load music
        music_path = resource_path("assets/music.wav")
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.settings.get("music_volume", 100) / 100)
        current_step += 1
        self.draw_loading_bar(current_step / total_steps)
        pygame.time.wait(200)

        # Start playing music after loading is complete
        pygame.mixer.music.play(-1)

    def load_sound(self, filename):
        path = resource_path(filename)
        return pygame.mixer.Sound(path) if os.path.exists(path) else None

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

    def draw_footer(self):
        footer_text = self.font_footer.render("РГ за истраживачко-развојне делатности, ЕТФ, 2025 ©", True, GOLD)
        self.screen.blit(footer_text, (self.screen_width - footer_text.get_width() - 10,
                                      self.screen_height - footer_text.get_height() - 10))

    def draw_background(self):
        current_width, current_height = self.screen.get_size()
        self.video_bg.update(0)
        frame = self.video_bg.get_frame(current_width, current_height)
        rect = frame.get_rect(center=(current_width // 2, current_height // 2))
        self.screen.blit(frame, rect)

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
            overlay.fill(GRAY)
            alpha = int((elapsed / duration) * 255) if fade_in else 255 - int((elapsed / duration) * 255)
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            clock.tick(60)

    def show_confetti(self, duration=3000):
        # Stop current background music and start victory music.
        pygame.mixer.music.stop()
        victory_music_path = resource_path("assets/victory.wav")
        if os.path.exists(victory_music_path):
            pygame.mixer.music.load(victory_music_path)
            pygame.mixer.music.play(-1)  # Loop indefinitely until game restart

        # Existing victory screen logic:
        if self.total_team1 == self.total_team2:
            winner = "Нерешено!"
        else:
            winner = f"Победник: {self.team1_name}" if self.total_team1 > self.total_team2 else f"Победник: {self.team2_name}"
        particles = [ConfettiParticle(random.randint(0, self.screen_width), 0) for _ in range(150)]
        start_time = pygame.time.get_ticks()
        final_font = load_font(BOLD_FONT_PATHS, FINAL_SIZE, "Roboto")
        while pygame.time.get_ticks() - start_time < duration:
            self.draw_background()
            for p in particles:
                p.update()
                p.draw(self.screen)
            final_msg = f"Коначни резултат - {self.team1_name}: {self.total_team1} | {self.team2_name}: {self.total_team2}"
            final_surf = final_font.render(final_msg, True, WHITE)
            winner_surf = final_font.render(winner, True, DARK_RED)
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
        header_font = load_font(BOLD_FONT_PATHS, HEADER_SIZE, "Roboto")
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
        big_font = load_font(BOLD_FONT_PATHS, BIG_SIZE, "Roboto")
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
        score_text = f"Резултат - {self.team1_name}: {self.total_team1} | {self.team2_name}: {self.total_team2}"
        self.screen.blit(self.font_regular.render(score_text, True, WHITE),
                         (self.screen_width - self.font_regular.size(score_text)[0] - 20, 20))
        active_text = f"Активни тим: {self.team1_name if active_team == 1 else self.team2_name}"
        color = RED if active_team == 1 else BLUE
        self.screen.blit(self.font_regular.render(active_text, True, color),
                         (self.screen_width - self.font_regular.size(active_text)[0] - 20, 60))
        question_font = self.font_question
        q_surf = question_font.render(question, True, BLACK)
        padding = 20
        q_box_width = q_surf.get_width() + padding * 2
        q_box_height = q_surf.get_height() + padding * 2
        gap = 20
        total_content_height = q_box_height + gap + len(answers) * 60
        question_box_y = (self.screen_height - total_content_height) // 2 + BOARD_VERTICAL_OFFSET
        q_rect = pygame.Rect((self.screen_width - q_box_width) // 2, question_box_y, q_box_width, q_box_height)
        shadow_rect = q_rect.move(3, 3)
        pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, q_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, q_rect, 2, border_radius=8)
        self.screen.blit(q_surf, (q_rect.x + padding, q_rect.y + padding))
        answer_y = question_box_y + q_box_height + gap
        rects = []
        current_time = pygame.time.get_ticks() / 500
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
                        shadow_rect = rect.move(3, 3)
                        pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=8)
                        pygame.draw.rect(self.screen, GRAY, rect, border_radius=8)
                        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
                        if answers[idx]["revealed"]:
                            pulse = int(5 * abs(math.sin(current_time)))
                            pygame.draw.rect(self.screen, YELLOW, rect.inflate(pulse, pulse), 4, border_radius=8)
                            text = f"{idx+1}. {answers[idx]['answer']} - {answers[idx]['points']}"
                        else:
                            text = f"{idx+1}."
                        text_surf = self.font_regular.render(text, True, BLACK)
                        self.screen.blit(text_surf, (rect.x + 10, rect.y + (50 - self.font_regular.get_height()) // 2))
                        rects.append(rect)
        else:
            for i, ans in enumerate(answers):
                rect = pygame.Rect(50, answer_y + i * 60, self.screen_width - 100, 50)
                shadow_rect = rect.move(3, 3)
                pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=8)
                pygame.draw.rect(self.screen, GRAY, rect, border_radius=8)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
                if ans["revealed"]:
                    pulse = int(5 * abs(math.sin(current_time)))
                    pygame.draw.rect(self.screen, YELLOW, rect.inflate(pulse, pulse), 4, border_radius=8)
                    text = f"{i+1}. {ans['answer']} - {ans['points']}"
                else:
                    text = f"{i+1}."
                text_surf = self.font_regular.render(text, True, BLACK)
                self.screen.blit(text_surf, (rect.x + 10, rect.y + (50 - self.font_regular.get_height()) // 2))
                rects.append(rect)
        now = pygame.time.get_ticks()
        time_to_next_glaze = random.randint(1500, 5000)
        if self.active_glaze_index is None and now - self.last_glaze_time >= time_to_next_glaze and len(rects) > 0:
            possible_indices = list(range(len(rects)))
            if self.last_glazed_index is not None and len(rects) > 1:
                if self.last_glazed_index in possible_indices:
                    possible_indices.remove(self.last_glazed_index)
            self.active_glaze_index = random.choice(possible_indices)
            self.glaze_start_time = now
            self.last_glaze_time = now
        if self.active_glaze_index is not None:
            progress = (now - self.glaze_start_time) / self.glaze_effect_duration
            if progress < 1.0:
                effect_width = 30
                effect_alpha = 150
                target_rect = rects[self.active_glaze_index]
                x_offset = int((target_rect.width - effect_width) * progress)
                glaze_surface = pygame.Surface((effect_width, target_rect.height), pygame.SRCALPHA)
                glaze_surface.fill((255, 255, 255, effect_alpha))
                self.screen.blit(glaze_surface, (target_rect.x + x_offset, target_rect.y))
            else:
                self.last_glazed_index = self.active_glaze_index
                self.active_glaze_index = None
                self.glaze_start_time = None
        strikes_text = f"Погрешних: {strikes}"
        self.screen.blit(self.font_regular.render(strikes_text, True, RED), (50, self.screen_height - 50))
        if state == "opponent":
            opp_text = "Шанса противника!"
            self.screen.blit(self.font_regular.render(opp_text, True, GRAY), (50, self.screen_height - 100))
        self.draw_footer()
        pygame.display.flip()
        return rects

    def settings_menu(self):
        orig_settings = {
            "screen_width": self.settings.get("screen_width", 1200),
            "screen_height": self.settings.get("screen_height", 800),
            "volume": self.settings.get("volume", 100),
            "music_volume": self.settings.get("music_volume", 100),
            "fullscreen": self.settings.get("fullscreen", False)
        }
        modal_w, modal_h = 600, 500
        current_width, current_height = self.screen.get_size()
        modal_x = (current_width - modal_w) // 2
        modal_y = (current_height - modal_h) // 2
        manual_width = str(self.settings.get("screen_width", 1200))
        manual_height = str(self.settings.get("screen_height", 800))
        sound_volume = self.settings.get("volume", 100)
        music_volume = self.settings.get("music_volume", 100)
        fullscreen = self.settings.get("fullscreen", False)
        width_active = False
        height_active = False
        font = load_font(FONT_PATHS, SETTINGS_SIZE, "Roboto")
        canceled = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == KEYDOWN:
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
                        canceled = True
                        running = False
                elif event.type == MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    rel_x = mx - modal_x
                    rel_y = my - modal_y
                    width_box = pygame.Rect(200, 20, 150, 30)
                    height_box = pygame.Rect(200, 70, 150, 30)
                    sound_slider = pygame.Rect(200, 120, 300, 20)
                    music_slider = pygame.Rect(200, 170, 300, 20)
                    checkbox = pygame.Rect(200, 220, 30, 30)
                    if width_box.collidepoint(rel_x, rel_y):
                        width_active = True
                        height_active = False
                    elif height_box.collidepoint(rel_x, rel_y):
                        height_active = True
                        width_active = False
                    elif sound_slider.collidepoint(rel_x, rel_y):
                        ratio = (rel_x - sound_slider.x) / sound_slider.width
                        new_volume = int(min(max(ratio, 0), 1) * 100)
                        if new_volume != sound_volume:
                            sound_volume = new_volume
                            if self.wrong_sound:
                                self.wrong_sound.set_volume(0.4 * (sound_volume / 100))
                                self.wrong_sound.play()
                    elif music_slider.collidepoint(rel_x, rel_y):
                        ratio = (rel_x - music_slider.x) / music_slider.width
                        new_volume = int(min(max(ratio, 0), 1) * 100)
                        if new_volume != music_volume:
                            music_volume = new_volume
                            pygame.mixer.music.set_volume(music_volume / 100)
                    elif checkbox.collidepoint(rel_x, rel_y):
                        fullscreen = not fullscreen
                    else:
                        width_active = False
                        height_active = False
                    save_rect = pygame.Rect(modal_w // 2 - 50, modal_h - 60, 100, 40)
                    if save_rect.collidepoint(rel_x, rel_y):
                        running = False
                elif event.type == MOUSEMOTION and event.buttons[0]:
                    mx, my = event.pos
                    rel_x = mx - modal_x
                    rel_y = my - modal_y
                    sound_slider = pygame.Rect(200, 120, 300, 20)
                    music_slider = pygame.Rect(200, 170, 300, 20)
                    if sound_slider.collidepoint(rel_x, rel_y):
                        ratio = (rel_x - sound_slider.x) / sound_slider.width
                        new_volume = int(min(max(ratio, 0), 1) * 100)
                        if new_volume != sound_volume:
                            sound_volume = new_volume
                            if self.wrong_sound:
                                self.wrong_sound.set_volume(0.4 * (sound_volume / 100))
                                self.wrong_sound.play()
                    elif music_slider.collidepoint(rel_x, rel_y):
                        ratio = (rel_x - music_slider.x) / music_slider.width
                        new_volume = int(min(max(ratio, 0), 1) * 100)
                        if new_volume != music_volume:
                            music_volume = new_volume
                            pygame.mixer.music.set_volume(music_volume / 100)
            modal = pygame.Surface((modal_w, modal_h))
            modal.fill((50, 50, 50))
            pygame.draw.rect(modal, WHITE, modal.get_rect(), 2)
            modal.blit(font.render("Ширина:", True, WHITE), (20, 20))
            pygame.draw.rect(modal, WHITE, (200, 20, 150, 30), 2)
            text_width = font.render(manual_width, True, WHITE)
            modal.blit(text_width, (205, 20))
            if width_active and (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = 205 + text_width.get_width() + 2
                pygame.draw.line(modal, WHITE, (cursor_x, 20), (cursor_x, 20 + text_width.get_height()), 2)
            modal.blit(font.render("Висина:", True, WHITE), (20, 70))
            pygame.draw.rect(modal, WHITE, (200, 70, 150, 30), 2)
            text_height = font.render(manual_height, True, WHITE)
            modal.blit(text_height, (205, 70))
            if height_active and (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = 205 + text_height.get_width() + 2
                pygame.draw.line(modal, WHITE, (cursor_x, 70), (cursor_x, 70 + text_height.get_height()), 2)
            modal.blit(font.render("Звук:", True, WHITE), (20, 120))
            sound_slider_rect = pygame.Rect(200, 120, 300, 20)
            pygame.draw.rect(modal, GRAY, sound_slider_rect)
            sound_ratio = sound_volume / 100
            knob_x = 200 + int(sound_ratio * 300) - 5
            pygame.draw.rect(modal, WHITE, (knob_x, 115, 10, 30))
            modal.blit(font.render("Музика:", True, WHITE), (20, 170))
            music_slider_rect = pygame.Rect(200, 170, 300, 20)
            pygame.draw.rect(modal, GRAY, music_slider_rect)
            music_ratio = music_volume / 100
            music_knob_x = 200 + int(music_ratio * 300) - 5
            pygame.draw.rect(modal, WHITE, (music_knob_x, 165, 10, 30))
            modal.blit(font.render("Пун екран:", True, WHITE), (20, 220))
            pygame.draw.rect(modal, WHITE, (200, 220, 30, 30), 2)
            if fullscreen:
                pygame.draw.rect(modal, WHITE, (203, 223, 24, 24))
            save_rect = pygame.Rect(modal_w // 2 - 50, modal_h - 60, 100, 30)
            pygame.draw.rect(modal, GRAY, save_rect)
            modal.blit(font.render("Сачувај", True, BLACK), (save_rect.x + 10, save_rect.y))
            modal.blit(font.render("Притисни ESC за повратак назад", True, WHITE), (modal_w // 2 - 180, modal_h - 30))
            self.screen.fill(BLACK)
            self.draw_background()
            self.screen.blit(modal, (modal_x, modal_y))
            pygame.display.flip()
            self.clock.tick(60)
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
        self.settings["volume"] = sound_volume
        self.settings["music_volume"] = music_volume
        self.settings["fullscreen"] = fullscreen
        self.save_settings()
        return self.settings

    def load_settings(self):
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=4)

    def choose_team(self, total_team1, total_team2):
        selecting = True
        current_x = -300
        target_x = 50
        last_time = pygame.time.get_ticks()
        while selecting:
            dt = pygame.time.get_ticks() - last_time
            last_time = pygame.time.get_ticks()
            current_x = min(target_x, current_x + dt * 0.5)
            
            # Instead of filling with black, draw the video background.
            self.draw_background()
            
            prompt1 = "Који тим игра у овој рунди?"
            prompt2 = f"Притисните 1 за {self.team1_name} или 2 за {self.team2_name}"
            self.screen.blit(self.font_regular.render(prompt1, True, WHITE), 
                            (current_x, self.screen_height // 2 - 60))
            self.screen.blit(self.font_regular.render(prompt2, True, WHITE), 
                            (current_x, self.screen_height // 2))
            
            scoreboard = f"Резултат уживо - {self.team1_name}: {total_team1} | {self.team2_name}: {total_team2}"
            self.screen.blit(self.font_regular.render(scoreboard, True, WHITE), 
                            (self.screen_width // 3, self.screen_height // 80))
            
            hint = self.font_regular.render("Притисни П да отвориш опције", True, WHITE)
            self.screen.blit(hint, (50, self.screen_height - 50))
            
            self.draw_footer()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == pygame.K_p:
                        # Open settings menu
                        self.settings = self.settings_menu()
                        pygame.mixer.music.set_volume(self.settings.get("music_volume", 100) / 100)
                        flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
                        self.screen = pygame.display.set_mode(
                            (self.settings["screen_width"], self.settings["screen_height"]), flags)
                        self.screen_width = self.settings["screen_width"]
                        self.screen_height = self.settings["screen_height"]
                        if self.wrong_sound:
                            self.wrong_sound.set_volume(0.4 * (self.settings.get("volume", 100) / 100))
                        if self.correct_sound:
                            self.correct_sound.set_volume(self.settings.get("volume", 100) / 100)
                        self.apply_font_settings()
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

    def apply_font_settings(self):
        """Update fonts after settings changes"""
        self.font_regular = load_font(FONT_PATHS, REGULAR_SIZE, "Roboto")
        self.font_question = load_font(BOLD_FONT_PATHS, QUESTION_SIZE, "Roboto")
        self.font_footer = load_font(FONT_PATHS, FOOTER_SIZE, "Roboto")

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
                self.video_bg.update(0)
                rects = self.draw_board(question, answers, strikes, state, active_team)
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit(); sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == pygame.K_p:
                            self.settings = self.settings_menu()
                            pygame.mixer.music.set_volume(self.settings.get("music_volume", 100) / 100)
                            flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
                            self.screen = pygame.display.set_mode((self.settings["screen_width"], self.settings["screen_height"]), flags)
                            self.screen_width = self.settings["screen_width"]
                            self.screen_height = self.settings["screen_height"]
                            if self.wrong_sound:
                                self.wrong_sound.set_volume(0.4 * (self.settings.get("volume", 100) / 100))
                            if self.correct_sound:
                                self.correct_sound.set_volume(self.settings.get("volume", 100) / 100)
                            self.apply_font_settings()
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
        return

if __name__ == "__main__":
    while True:
        FamilyFeudGame().run()
