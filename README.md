# Породични Дуел! РГДЕВ - ЕТФ


![FF_SCREEN_ETF](https://i.imgur.com/0G5n7JX.png)

**Породични Дуел!** is a Family Feud–style game developed using Python and [Pygame](https://www.pygame.org/). The game is designed for two teams to compete by guessing survey answers based on questions loaded from text files. This project is tailored for educational or event purposes at the Faculty of Electrical Engineering (ЕТФ) and uses Serbian for in-game texts and messages.

## Features

- **Family Feud Game Mechanics:**  
  Two teams compete to reveal correct answers and accumulate points.

- **Dynamic Rounds:**  
  The game is divided into multiple rounds with different questions loaded from files.

- **Interactive UI:**  
  The interface features a dynamic background, responsive buttons, and animated effects.

- **In-Game Options Menu:**  
  Press **P** during gameplay to open the options menu. Adjust the screen resolution, toggle fullscreen mode, and change the volume using sliders and a checkbox. Changes are auto-applied and saved in `settings.json`.

- **Sound Effects:**  
  Correct answers and wrong attempts are signaled with distinct sound effects (volume adjustable via the options menu).

- **Score Tracking:**  
  Scores for both teams are displayed on-screen and stored in a SQLite database for each round.

- **Footer Credits:**  
  A footer in small, italic, golden text is displayed on every screen.

## Installation

### Prerequisites

- Python 3.12 or later
- [Pygame](https://www.pygame.org/) (version 2.6.1 or later)
- SQLite3 (Python’s built-in `sqlite3` module is used)

### Install Pygame

```bash
pip install pygame

### **Project Files**

📁 project-folder/
│-- 📄 main.py              # The main game script
│-- 📄 settings.json        # Stores user settings (auto-created/updated)
│-- 📄 teams.txt            # Contains team names (each on a new line)
│-- 📁 assets/              # Folder with assets (background, sounds, etc.)
│   │-- 🎵 correct.wav      # Sound effect for correct answers
│   │-- 🎵 wrong.wav        # Sound effect for wrong answers
│   │-- 🖼️ background.jpg   # Background image
│-- 📁 questions/           # Folder with round files
│   │-- 📄 round1.txt       # Text file containing questions and answers
│   │-- 📄 round2.txt       # More rounds...

Each file in questions/ should be formatted as follows:
```Question goes here
Answer1, Points1
Answer2, Points2
...
```

### Usage

## Start the Game
- Run the main Python script:
python main.py
or, if applicable:
py main.py

## Team Selection
At the beginning of each round, choose the active team by pressing 1 or 2.
A hint at the bottom left reminds you:
“Притисни П да отвориш опције”

## In-Game Options
- Press P at any time to open the options menu.
- Adjust:
 -- Screen resolution
 -- Fullscreen mode
 -- Volume using sliders and a checkbox
 - A hint at the bottom of the options screen says:
 “Притисни ЕСЦ за повратак у игру”
- Changes apply immediately and save in settings.json.
- 
## Answering Questions
Input the number corresponding to the answer you want to reveal.
Press X to mark a wrong attempt.
The game automatically updates scores based on revealed answers.

## Game Over
At the end of all rounds, the final scores for both teams are displayed before the game exits.

### Credits
Developed for the Electrical Engineering Faculty (ЕТФ) with support from the Research and Development work group.

© 2025 – РГ за истраживачко-развојне делатности, ЕТФ
