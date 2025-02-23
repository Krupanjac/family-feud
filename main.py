import pygame
import sys
import sqlite3
import os
import math
import json
from pygame.locals import KEYDOWN, K_ESCAPE, K_x, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

# ----------------- Default Settings -----------------
DEFAULT_SETTINGS = {
    "screen_width": 1200,
    "screen_height": 800,
    "fullscreen": False,
    "volume": 100  # 100% volume by default
}

# Colors and fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (212, 175, 55)  # golden color for footer
REGULAR = 36
QUESTION = 50

# Global screen dimensions (will be updated via settings)
SCREEN_WIDTH = DEFAULT_SETTINGS["screen_width"]
SCREEN_HEIGHT = DEFAULT_SETTINGS["screen_height"]

# Animation parameters
ZOOM_SPEED = 0.0007  # Slower zoom speed

# ----------------- Helper: Draw Footer -----------------
def draw_footer(screen):
    # Create a small italic font for credits
    footer_font = pygame.font.SysFont(None, 20, italic=True)
    footer_text = footer_font.render("РГ за истраживачко-развојне делатности, ЕТФ, 2025 ©", True, GOLD)
    # Position the text in the bottom right with a small margin
    screen.blit(footer_text, (SCREEN_WIDTH - footer_text.get_width() - 10,
                              SCREEN_HEIGHT - footer_text.get_height() - 10))

# ----------------- Settings I/O -----------------
def load_settings():
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

# ----------------- Settings Menu -----------------
def settings_menu(screen, settings):
    clock = pygame.time.Clock()
    menu_running = True

    # Get current settings values:
    current_width = settings.get("screen_width", 1200)
    current_height = settings.get("screen_height", 800)
    current_volume = settings.get("volume", 100)
    current_fullscreen = settings.get("fullscreen", False)

    # Define slider ranges
    width_min, width_max = 800, 1920
    height_min, height_max = 600, 1080
    volume_min, volume_max = 0, 100

    # Slider dimensions
    slider_length = 300
    slider_height = 20

    # Positions for options (vertical spacing)
    start_x = 100
    start_y = 100
    option_spacing = 80

    # Calculate positions for texts and controls
    width_text_pos = (start_x, start_y)
    width_slider_pos = (start_x + 250, start_y + 10)
    
    height_text_pos = (start_x, start_y + option_spacing)
    height_slider_pos = (start_x + 250, start_y + option_spacing + 10)
    
    volume_text_pos = (start_x, start_y + 2 * option_spacing)
    volume_slider_pos = (start_x + 250, start_y + 2 * option_spacing + 10)
    
    fullscreen_text_pos = (start_x, start_y + 3 * option_spacing)
    checkbox_pos = (start_x + 250, start_y + 3 * option_spacing)

    font = pygame.font.SysFont(None, 40)

    while menu_running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    menu_running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    mouse_x, mouse_y = event.pos
                    # Define slider rectangles
                    width_slider_rect = pygame.Rect(width_slider_pos[0], width_slider_pos[1], slider_length, slider_height)
                    height_slider_rect = pygame.Rect(height_slider_pos[0], height_slider_pos[1], slider_length, slider_height)
                    volume_slider_rect = pygame.Rect(volume_slider_pos[0], volume_slider_pos[1], slider_length, slider_height)
                    # Fullscreen checkbox rectangle (30x30)
                    checkbox_rect = pygame.Rect(checkbox_pos[0], checkbox_pos[1], 30, 30)

                    if width_slider_rect.collidepoint(mouse_x, mouse_y):
                        rel_x = mouse_x - width_slider_rect.x
                        ratio = max(0, min(1, rel_x / slider_length))
                        current_width = int(width_min + ratio * (width_max - width_min))
                    elif height_slider_rect.collidepoint(mouse_x, mouse_y):
                        rel_x = mouse_x - height_slider_rect.x
                        ratio = max(0, min(1, rel_x / slider_length))
                        current_height = int(height_min + ratio * (height_max - height_min))
                    elif volume_slider_rect.collidepoint(mouse_x, mouse_y):
                        rel_x = mouse_x - volume_slider_rect.x
                        ratio = max(0, min(1, rel_x / slider_length))
                        current_volume = int(volume_min + ratio * (volume_max - volume_min))
                    elif checkbox_rect.collidepoint(mouse_x, mouse_y):
                        current_fullscreen = not current_fullscreen
            elif event.type == MOUSEMOTION:
                if event.buttons[0]:
                    mouse_x, mouse_y = event.pos
                    width_slider_rect = pygame.Rect(width_slider_pos[0], width_slider_pos[1], slider_length, slider_height)
                    height_slider_rect = pygame.Rect(height_slider_pos[0], height_slider_pos[1], slider_length, slider_height)
                    volume_slider_rect = pygame.Rect(volume_slider_pos[0], volume_slider_pos[1], slider_length, slider_height)
                    if width_slider_rect.collidepoint(mouse_x, mouse_y):
                        rel_x = mouse_x - width_slider_rect.x
                        ratio = max(0, min(1, rel_x / slider_length))
                        current_width = int(width_min + ratio * (width_max - width_min))
                    elif height_slider_rect.collidepoint(mouse_x, mouse_y):
                        rel_x = mouse_x - height_slider_rect.x
                        ratio = max(0, min(1, rel_x / slider_length))
                        current_height = int(height_min + ratio * (height_max - height_min))
                    elif volume_slider_rect.collidepoint(mouse_x, mouse_y):
                        rel_x = mouse_x - volume_slider_rect.x
                        ratio = max(0, min(1, rel_x / slider_length))
                        current_volume = int(volume_min + ratio * (volume_max - volume_min))
        
        # Draw a semi-transparent overlay covering the entire screen
        overlay = pygame.Surface((settings["screen_width"], settings["screen_height"]), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Render texts for each option
        width_text = font.render(f"Screen Width: {current_width}", True, WHITE)
        height_text = font.render(f"Screen Height: {current_height}", True, WHITE)
        volume_text = font.render(f"Volume: {current_volume}%", True, WHITE)
        fullscreen_text = font.render("Fullscreen", True, WHITE)
        screen.blit(width_text, width_text_pos)
        screen.blit(height_text, height_text_pos)
        screen.blit(volume_text, volume_text_pos)
        screen.blit(fullscreen_text, fullscreen_text_pos)
        
        # Draw slider bars
        def draw_slider(x, y, length, value, min_val, max_val):
            pygame.draw.rect(screen, GRAY, (x, y, length, slider_height))
            ratio = (value - min_val) / (max_val - min_val)
            knob_x = x + int(ratio * length) - 5
            knob_rect = pygame.Rect(knob_x, y - 5, 10, slider_height + 10)
            pygame.draw.rect(screen, WHITE, knob_rect)
        
        draw_slider(width_slider_pos[0], width_slider_pos[1], slider_length, current_width, width_min, width_max)
        draw_slider(height_slider_pos[0], height_slider_pos[1], slider_length, current_height, height_min, height_max)
        draw_slider(volume_slider_pos[0], volume_slider_pos[1], slider_length, current_volume, volume_min, volume_max)
        
        # Draw the fullscreen checkbox
        checkbox_rect = pygame.Rect(checkbox_pos[0], checkbox_pos[1], 30, 30)
        pygame.draw.rect(screen, WHITE, checkbox_rect, 2)  # draw the border
        if current_fullscreen:
            pygame.draw.rect(screen, WHITE, checkbox_rect.inflate(-6, -6))
        
        # Add hint for settings menu at bottom center
        hint_text = font.render("Притисни ЕСЦ за повратак у игру", True, WHITE)
        screen.blit(hint_text, (start_x, settings["screen_height"] - 50))
        
        # Draw footer credit in the bottom right corner
        draw_footer(screen)
        
        # Auto-update the settings (no "Apply" button)
        settings["screen_width"] = current_width
        settings["screen_height"] = current_height
        settings["volume"] = current_volume
        settings["fullscreen"] = current_fullscreen

        pygame.display.flip()
        clock.tick(60)

    # Save settings when exiting the menu
    save_settings(settings)
    return settings

# ----------------- Game Functions -----------------
class BackgroundEffect:
    def __init__(self, base_background):
        self.base_background = base_background
        self.original_background = base_background.copy() if base_background else None
        self.zoom_phase = 0
        
    def update(self, dt):
        self.zoom_phase = (self.zoom_phase + ZOOM_SPEED * dt) % math.pi
        
    def get_transformed_bg(self):
        if not self.original_background:
            return None
        scale = 1.0 + 0.1 * math.sin(self.zoom_phase)
        scaled_bg = pygame.transform.smoothscale(self.original_background, 
            (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)))
        return scaled_bg

def load_background():
    bg_filename = "assets/background.jpg"
    if os.path.exists(bg_filename):
        bg = pygame.image.load(bg_filename).convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return bg
    return None

def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None

def draw_background(screen, bg_effect):
    if bg_effect.base_background:
        scaled_bg = bg_effect.get_transformed_bg()
        bg_rect = scaled_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(scaled_bg, bg_rect)

def load_team_names():
    filename = "teams.txt"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if len(lines) >= 2:
                return lines[0], lines[1]
    return "Тим1", "Тим2"

def load_round_file(round_num):
    filename = f"questions/round{round_num}.txt"
    if not os.path.exists(filename):
        print(f"Фајл {filename} није пронађен.")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        return None
    question = lines[0]
    answers = []
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) == 2:
            answer_text = parts[0].strip()
            try:
                points = int(parts[1].strip())
            except ValueError:
                points = 0
            answers.append({"answer": answer_text, "points": points, "revealed": False})
    return question, answers

def init_db():
    db_filename = "family_feud.db"
    if os.path.exists(db_filename):
        os.remove(db_filename)
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            round_number INTEGER PRIMARY KEY,
            team1_points INTEGER,
            team2_points INTEGER
        )
    """)
    conn.commit()
    return conn

def save_round_result(conn, round_number, team1_points, team2_points):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rounds (round_number, team1_points, team2_points) VALUES (?, ?, ?)",
        (round_number, team1_points, team2_points)
    )
    conn.commit()

def show_wrong_feedback(screen, clock, wrong_sound):
    if wrong_sound:
        wrong_sound.play()
    
    big_font = pygame.font.SysFont(None, 300)
    orig_x_text = big_font.render("X", True, RED).convert_alpha()
    start_time = pygame.time.get_ticks()
    duration = 1000
    while True:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed >= duration:
            break
        alpha = max(255 - int(255 * (elapsed / duration)), 0)
        scale = 1.0 + 0.5 * (elapsed / duration)
        new_width = int(orig_x_text.get_width() * scale)
        new_height = int(orig_x_text.get_height() * scale)
        scaled_x_text = pygame.transform.smoothscale(orig_x_text, (new_width, new_height))
        scaled_x_text.set_alpha(alpha)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))
        x_rect = scaled_x_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        overlay.blit(scaled_x_text, x_rect)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def draw_board(screen, regular_font, question_font, question, answers, strikes, state, 
               total_team1, total_team2, active_team, team1_name, team2_name, bg_effect):
    screen.fill(BLACK)
    draw_background(screen, bg_effect)
    
    score_text = f"Резултат - {team1_name}: {total_team1} | {team2_name}: {total_team2}"
    score_surf = regular_font.render(score_text, True, WHITE)
    screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 20, 20))
    
    active_text = f"Активни тим: {team1_name if active_team == 1 else team2_name}"
    color = RED if active_team == 1 else BLUE
    active_surf = regular_font.render(active_text, True, color)
    screen.blit(active_surf, (SCREEN_WIDTH - active_surf.get_width() - 20, 60))
    
    question_surf = question_font.render(question, True, WHITE)
    question_height = question_surf.get_height()
    extra_spacing = 20

    num_answers = len(answers)
    box_height = 50
    spacing = 10

    if num_answers > 4:
        rows = math.ceil(num_answers / 2)
        column_width = (SCREEN_WIDTH - 150) // 2
        total_answers_height = rows * (box_height + spacing)
    else:
        column_width = SCREEN_WIDTH - 100
        total_answers_height = num_answers * (box_height + spacing)

    total_content_height = question_height + extra_spacing + total_answers_height
    start_y = (SCREEN_HEIGHT - total_content_height) // 2
    
    screen.blit(question_surf, (SCREEN_WIDTH // 2 - question_surf.get_width() // 2, start_y))
    
    answer_start_y = start_y + question_height + extra_spacing
    rects = []

    if num_answers > 4:
        rows = math.ceil(num_answers / 2)
        left_x = 50
        right_x = 50 + column_width + 50
        for row in range(rows):
            y = answer_start_y + row * (box_height + spacing)
            index_left = row * 2
            if index_left < num_answers:
                rect = pygame.Rect(left_x, y, column_width, box_height)
                pygame.draw.rect(screen, GRAY, rect)
                ans = answers[index_left]
                text = f"{index_left+1}. {ans['answer']} - {ans['points']}" if ans["revealed"] else f"{index_left+1}."
                text_surf = regular_font.render(text, True, BLACK)
                screen.blit(text_surf, (rect.x + 10, rect.y + (box_height - text_surf.get_height()) // 2))
                rects.append(rect)
            index_right = row * 2 + 1
            if index_right < num_answers:
                rect = pygame.Rect(right_x, y, column_width, box_height)
                pygame.draw.rect(screen, GRAY, rect)
                ans = answers[index_right]
                text = f"{index_right+1}. {ans['answer']} - {ans['points']}" if ans["revealed"] else f"{index_right+1}."
                text_surf = regular_font.render(text, True, BLACK)
                screen.blit(text_surf, (rect.x + 10, rect.y + (box_height - text_surf.get_height()) // 2))
                rects.append(rect)
    else:
        for i, ans in enumerate(answers):
            rect = pygame.Rect(50, answer_start_y + i * (box_height + spacing), column_width, box_height)
            pygame.draw.rect(screen, GRAY, rect)
            text = f"{i+1}. {ans['answer']} - {ans['points']}" if ans["revealed"] else f"{i+1}."
            text_surf = regular_font.render(text, True, BLACK)
            screen.blit(text_surf, (rect.x + 10, rect.y + (box_height - text_surf.get_height()) // 2))
            rects.append(rect)
    
    strikes_text = f"Погрешних: {strikes}"
    strikes_surf = regular_font.render(strikes_text, True, RED)
    screen.blit(strikes_surf, (50, SCREEN_HEIGHT - 50))
    
    if state == "opponent":
        message = "Шанса противника!"
        message_surf = regular_font.render(message, True, BLUE)
        screen.blit(message_surf, (50, SCREEN_HEIGHT - 100))
    
    # Draw footer credit
    draw_footer(screen)
    
    pygame.display.flip()
    return rects

def choose_team(screen, font, clock, total_team1, total_team2, team1_name, team2_name, bg_effect, correct_sound, wrong_sound, settings):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    selecting = True
    last_time = pygame.time.get_ticks()
    
    while selecting:
        dt = pygame.time.get_ticks() - last_time
        last_time = pygame.time.get_ticks()
        bg_effect.update(dt)
        
        screen.fill(BLACK)
        draw_background(screen, bg_effect)
        prompt_line1 = "Који тим игра у овој рунди?"
        prompt_line2 = f"Притисните 1 за {team1_name} или 2 за {team2_name}"
        line1_surf = font.render(prompt_line1, True, WHITE)
        line2_surf = font.render(prompt_line2, True, WHITE)
        screen.blit(line1_surf, (50, SCREEN_HEIGHT // 2 - 60))
        screen.blit(line2_surf, (50, SCREEN_HEIGHT // 2))
        
        scoreboard = f"Резултат уживо - {team1_name}: {total_team1} | {team2_name}: {total_team2}"
        scoreboard_surf = font.render(scoreboard, True, WHITE)
        screen.blit(scoreboard_surf, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 80))
        
        # Add team-selection hint at bottom left
        hint = font.render("Притисни П да отвориш опције", True, WHITE)
        screen.blit(hint, (50, SCREEN_HEIGHT - 50))
        draw_footer(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == pygame.K_p:
                    settings = settings_menu(screen, settings)
                    flags = pygame.FULLSCREEN if settings["fullscreen"] else 0
                    screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]), flags)
                    SCREEN_WIDTH = settings["screen_width"]
                    SCREEN_HEIGHT = settings["screen_height"]
                    # Update sound volumes immediately after changing settings
                    if wrong_sound:
                        wrong_sound.set_volume(0.4 * (settings.get("volume", 100) / 100))
                    if correct_sound:
                        correct_sound.set_volume(settings.get("volume", 100) / 100)
                    font = pygame.font.SysFont(None, REGULAR)
                    continue
                elif event.unicode == '1':
                    if correct_sound: correct_sound.play()
                    return 1, settings, screen
                elif event.unicode == '2':
                    if correct_sound: correct_sound.play()
                    return 2, settings, screen
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                pass
        clock.tick(60)
    return 1, settings, screen

# ----------------- Main Game Loop -----------------
def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    pygame.mixer.init()

    settings = load_settings()
    SCREEN_WIDTH = settings["screen_width"]
    SCREEN_HEIGHT = settings["screen_height"]
    flags = pygame.FULLSCREEN if settings["fullscreen"] else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("Породични Дуел! РГДЕВ - ЕТФ")
    
    regular_font = pygame.font.SysFont(None, REGULAR)
    question_font = pygame.font.SysFont(None, QUESTION)
    clock = pygame.time.Clock()
    
    correct_sound = load_sound("assets/correct.wav")
    wrong_sound = load_sound("assets/wrong.wav")
    if wrong_sound:
        wrong_sound.set_volume(0.4 * (settings.get("volume", 100) / 100))
    if correct_sound:
        correct_sound.set_volume(settings.get("volume", 100) / 100)
    
    conn = init_db()
    team1_name, team2_name = load_team_names()
    background = load_background()
    bg_effect = BackgroundEffect(background)

    total_team1 = 0
    total_team2 = 0

    for round_num in range(1, 6):
        active_team, settings, screen = choose_team(screen, regular_font, clock, total_team1, total_team2, 
                                                      team1_name, team2_name, bg_effect, correct_sound, wrong_sound, settings)
        if active_team == 1:
            team1_round_points = 0
            team2_round_points = 0
        else:
            team2_round_points = 0
            team1_round_points = 0

        data = load_round_file(round_num)
        if data is None:
            print(f"Грешка у фајлу за рунду {round_num}.")
            continue
        question, answers = data
        
        strikes = 0
        state = "active"
        last_time = pygame.time.get_ticks()

        while True:
            dt = pygame.time.get_ticks() - last_time
            last_time = pygame.time.get_ticks()
            bg_effect.update(dt)
            
            rects = draw_board(screen, regular_font, question_font, question, answers, 
                               strikes, state, total_team1, total_team2, active_team, 
                               team1_name, team2_name, bg_effect)
            
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == pygame.K_p:
                    settings = settings_menu(screen, settings)
                    flags = pygame.FULLSCREEN if settings["fullscreen"] else 0
                    screen = pygame.display.set_mode((settings["screen_width"], settings["screen_height"]), flags)
                    SCREEN_WIDTH = settings["screen_width"]
                    SCREEN_HEIGHT = settings["screen_height"]
                    if wrong_sound:
                        wrong_sound.set_volume(0.4 * (settings.get("volume", 100) / 100))
                    if correct_sound:
                        correct_sound.set_volume(settings.get("volume", 100) / 100)
                    continue
                elif event.type == KEYDOWN:
                    if state == "active":
                        if event.unicode.isdigit():
                            index = int(event.unicode) - 1
                            if 0 <= index < len(answers) and not answers[index]["revealed"]:
                                answers[index]["revealed"] = True
                                if correct_sound: correct_sound.play()
                                if active_team == 1:
                                    team1_round_points += answers[index]["points"]
                                else:
                                    team2_round_points += answers[index]["points"]
                        elif event.key == pygame.K_x:
                            show_wrong_feedback(screen, clock, wrong_sound)
                            strikes += 1
                            if strikes >= 3:
                                if not all(ans["revealed"] for ans in answers):
                                    state = "opponent"
                                else:
                                    state = "round_over"
                    elif state == "opponent":
                        if event.unicode.isdigit():
                            index = int(event.unicode) - 1
                            if 0 <= index < len(answers) and not answers[index]["revealed"]:
                                answers[index]["revealed"] = True
                                if correct_sound: correct_sound.play()
                                if active_team == 1:
                                    team2_round_points = team1_round_points + answers[index]["points"]
                                    team1_round_points = 0
                                else:
                                    team1_round_points = team2_round_points + answers[index]["points"]
                                    team2_round_points = 0
                                state = "round_over"
                        elif event.key == pygame.K_x:
                            show_wrong_feedback(screen, clock, wrong_sound)
                            state = "round_over"
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(pos):
                            if state == "active" and not answers[i]["revealed"]:
                                answers[i]["revealed"] = True
                                if correct_sound: correct_sound.play()
                                if active_team == 1:
                                    team1_round_points += answers[i]["points"]
                                else:
                                    team2_round_points += answers[i]["points"]
                            elif state == "opponent" and not answers[i]["revealed"]:
                                answers[i]["revealed"] = True
                                if correct_sound: correct_sound.play()
                                if active_team == 1:
                                    team2_round_points = team1_round_points + answers[i]["points"]
                                    team1_round_points = 0
                                else:
                                    team1_round_points = team2_round_points + answers[i]["points"]
                                    team2_round_points = 0
                                state = "round_over"
            
            if state == "active" and all(ans["revealed"] for ans in answers):
                state = "round_over"
                
            if state == "round_over":
                draw_board(screen, regular_font, question_font, question, answers, 
                           strikes, state, total_team1, total_team2, active_team, 
                           team1_name, team2_name, bg_effect)
                if active_team == 1:
                    msg = f"Рунда {round_num} је завршена. {team1_name}: {team1_round_points} | {team2_name}: {team2_round_points}"
                else:
                    msg = f"Рунда {round_num} је завршена. {team2_name}: {team2_round_points} | {team1_name}: {team1_round_points}"
                msg_surf = regular_font.render(msg, True, WHITE)
                screen.blit(msg_surf, (50, SCREEN_HEIGHT - 150))
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        elif event.type in (KEYDOWN, MOUSEBUTTONDOWN):
                            waiting = False
                    clock.tick(60)
                    
                if active_team == 1:
                    total_team1 += team1_round_points
                    total_team2 += team2_round_points
                else:
                    total_team2 += team2_round_points
                    total_team1 += team1_round_points
                    
                save_round_result(conn, round_num, total_team1, total_team2)
                break

            clock.tick(60)

    screen.fill(BLACK)
    draw_background(screen, bg_effect)
    final_msg = f"Игра је завршена! Коначни резултати - {team1_name}: {total_team1} | {team2_name}: {total_team2}"
    final_surf = regular_font.render(final_msg, True, WHITE)
    screen.blit(final_surf, (SCREEN_WIDTH // 2 - final_surf.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(5000)
    conn.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
