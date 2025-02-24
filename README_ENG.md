# Породични Дуел! РГДЕВ - ЕТФ

![FF_SCREEN_ETF](https://i.imgur.com/VnjK0Ve.png)
![FF_SCREEN2_ETF](https://i.imgur.com/UbtEK7J.png)

**Породични Дуел!** is a Family Feud–style game developed in Python using [Pygame](https://www.pygame.org/). Two teams compete to reveal survey answers, accumulate points, and win rounds by answering questions loaded from text files. This project is designed for educational or event purposes at the Faculty of Electrical Engineering (ЕТФ) and uses Serbian for all in-game texts.

---

## Features

- **Family Feud Mechanics:**  
  Two teams compete by revealing answers to survey questions. Points are awarded based on the revealed answers.

- **Dynamic Rounds and Questions:**  
  The game is divided into multiple rounds. Each round loads a new question and its corresponding answers from files located in the `questions/` folder.

- **Interactive User Interface:**  
  Enjoy a dynamic background, animated effects (such as fading transitions, screen shakes, and confetti celebrations), and a responsive board for revealing answers.

- **In-Game Options Menu:**  
  Customize your experience by changing screen resolution, toggling fullscreen mode, and adjusting sound settings—all while the game is running.

- **Real-Time Score Tracking:**  
  Team scores are continuously updated and stored in a SQLite database for every round.

- **Footer Credits:**  
  Every screen displays a footer crediting the team behind the game.

---

## Installation

### Prerequisites

- **Python 3.12 or later**
- **[Pygame](https://www.pygame.org/) (version 2.6.1 or later)**
- **SQLite3:** (Python’s built-in `sqlite3` module is used for score tracking)

### Install Pygame

Run the following command in your terminal or command prompt:

```bash
pip install pygame
```

### Project Files Structure

```plaintext
project-folder/
│-- main.py              # Main game script
│-- settings.json        # Stores user settings (auto-created/updated)
│-- teams.txt            # Contains team names (each on a new line)
│-- assets/              # Folder with assets (images, sounds, etc.)
│   │-- correct.wav      # Sound effect for correct answers
│   │-- wrong.wav        # Sound effect for wrong answers
│   │-- background.jpg   # Background image
│   │-- favicon.png      # Game icon
│-- questions/           # Folder with round files
│   │-- round1.txt       # File with a question and its answers
│   │-- round2.txt       # Additional rounds…
```

Each file in the `questions/` folder should be formatted as follows:

```plaintext
Question goes here
Answer1, Points1
Answer2, Points2
...
```

---

## How to Play

### Starting the Game

- Run the main Python script:
  ```bash
  python main.py
  ```
  or (if applicable):
  ```bash
  py main.py
  ```

### Team Selection

At the beginning of each round, you will see a prompt asking:
- **"Који тим игра у овој рунди?"**  
  Press **1** for the first team or **2** for the second team.  
  A hint at the bottom left reminds you:  
  **"Притисни П да отвориш опције"**

### Answering Questions

- **Revealing an Answer:**
  - **Keyboard:** Press the digit corresponding to the answer (e.g., 1, 2, 3, etc.) to reveal it.
  - **Mouse:** Click on the answer box to reveal the answer.

- **Marking a Wrong Answer:**
  - **Keyboard:** Press the **X** key to indicate a wrong attempt.
  - Each wrong attempt is signaled with a screen shake and an animated “X”. After three wrong attempts (if not all answers have been revealed), control may pass to the opposing team.

### In-Game Options Menu

You can adjust settings during gameplay. To access the options menu:

- **Press P** at any time while playing.

#### Options Menu Controls

- **Screen Resolution:**
  - Click on the text boxes labeled “Ширина:” (Width) and “Висина:” (Height).
  - Use your keyboard to type in the new dimensions.
  
- **Volume Controls:**
  - **Sound Volume:** Click or drag on the sound slider to adjust the overall game volume. A short sound clip (if available) gives immediate feedback.
  - **Music Volume:** Adjust the background music volume using the corresponding slider.
  
- **Fullscreen Mode:**
  - Toggle fullscreen on or off by clicking the checkbox next to “Пун екран:” (Fullscreen).
  
- **Saving Changes:**
  - Click the “Сачувај” (Save) button to apply and save your settings to `settings.json`.
  - To cancel changes and return to the game, press **ESC**.

### Game Transitions and Effects

- **Fade Transitions:**  
  The game uses smooth fade-in and fade-out transitions between rounds and when switching teams.
  
- **Dynamic Background and Animations:**  
  A continuously animated background and a “glaze” effect on answer boxes add visual flair to the game.

- **Confetti Celebration:**  
  At the end of all rounds, a confetti animation displays the final scores and declares the winner.

---

## Additional Controls & Shortcuts

- **Quit Game:**  
  At any point, press **ESC** (or close the window) to exit the game.

- **Mouse vs. Keyboard:**  
  You can choose between using the mouse or keyboard for interactions:
  - **Mouse:** Click on interactive elements (answers, options menu fields, sliders).
  - **Keyboard:** Use numeric keys to reveal answers, **X** to mark wrong answers, **P** for options, and **ESC** to exit or cancel.

---

## Credits

Developed for the Electrical Engineering Faculty (ЕТФ) with support from the Research and Development work group.  
© 2025 – РГ за истраживачко-развојне делатности, ЕТФ

---

This detailed guide should help you get the most out of the game—whether you’re playing, adjusting settings, or just exploring the various interactive features. Enjoy the game!
