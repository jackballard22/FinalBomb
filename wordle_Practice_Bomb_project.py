import tkinter as tk
import random

# --- CONFIG ---
WORD_LENGTH = 5
MAX_ATTEMPTS = 6
WORD_LIST = ["APPLE", "BRAIN", "CHAIR", "LIGHT", "MONEY", "WATER", "PLANT", "HOUSE", "MUSIC", "TRAIN"]

# --- GAME SETUP ---
answer = random.choice(WORD_LIST)
attempt = 0
guesses = []

# --- GUI SETUP ---
root = tk.Tk()
root.title("Tkinter Wordle")
root.geometry("400x600")
root.config(bg="#121213")

# Fonts and colors
FONT = ("Helvetica", 18, "bold")
COLORS = {
    "correct": "#538d4e",   # green
    "present": "#b59f3b",   # yellow
    "absent": "#3a3a3c",    # gray
    "empty": "#121213"
}

# --- GRID ---
labels = []
for row in range(MAX_ATTEMPTS):
    row_labels = []
    for col in range(WORD_LENGTH):
        lbl = tk.Label(root, text="", width=4, height=2, font=FONT, 
                       relief="solid", bg=COLORS["empty"], fg="white", bd=1)
        lbl.grid(row=row, column=col, padx=3, pady=3)
        row_labels.append(lbl)
    labels.append(row_labels)

# --- INPUT FIELD ---
entry = tk.Entry(root, font=("Helvetica", 16), justify="center")
entry.grid(row=MAX_ATTEMPTS + 1, column=0, columnspan=3, pady=20)

def submit_guess():
    global attempt
    guess = entry.get().strip().upper()
    entry.delete(0, tk.END)

    if len(guess) != WORD_LENGTH or not guess.isalpha():
        return  # Invalid guess, ignore

    if attempt >= MAX_ATTEMPTS:
        return  # Game over

    # --- Color checking ---
    result_colors = []
    answer_chars = list(answer)
    guess_chars = list(guess)

    # Green pass
    for i in range(WORD_LENGTH):
        if guess_chars[i] == answer_chars[i]:
            result_colors.append("correct")
            answer_chars[i] = None
        else:
            result_colors.append(None)

    # Yellow/gray pass
    for i in range(WORD_LENGTH):
        if result_colors[i] is None:
            if guess_chars[i] in answer_chars:
                result_colors[i] = "present"
                answer_chars[answer_chars.index(guess_chars[i])] = None
            else:
                result_colors[i] = "absent"

    # --- Update GUI ---
    for i in range(WORD_LENGTH):
        lbl = labels[attempt][i]
        lbl.config(text=guess[i], bg=COLORS[result_colors[i]])

    # --- Check win/lose ---
    if guess == answer:
        result_label.config(text=f"You got it! The word was {answer}", fg="#00ff00")
        entry.config(state="disabled")
        return
    elif attempt == MAX_ATTEMPTS - 1:
        result_label.config(text=f"Out of tries! The word was {answer}", fg="red")
        entry.config(state="disabled")

    attempt += 1

# --- SUBMIT BUTTON ---
submit_btn = tk.Button(root, text="Submit", command=submit_guess, font=("Helvetica", 14))
submit_btn.grid(row=MAX_ATTEMPTS + 1, column=3, columnspan=2)

# --- RESULT LABEL ---
result_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#121213", fg="white")
result_label.grid(row=MAX_ATTEMPTS + 2, column=0, columnspan=WORD_LENGTH, pady=20)

root.mainloop()
