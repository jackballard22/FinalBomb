import tkinter as tk
import random


# =========================
#   CONFIGURATION
# =========================

WIRE_COLORS = ["BLUE", "PURPLE", "GREY", "WHITE", "BLACK"]

# Secret correct order – change this to whatever order you want
WIRE_ORDER = ["BLUE", "WHITE", "PURPLE", "GREY", "BLACK"]

# Hints for each step in the order (same length as WIRE_ORDER)
WIRE_HINTS = [
    "First wire: the color of the sky.",
    "Second wire: the lightest of them all.",
    "Third wire: a royal color.",
    "Fourth wire: the color between black and white.",
    "Last wire: the darkest color."
]

# =========================
#   STATE VARIABLES
# =========================

wire_step = 0        # how many correct wires have been clicked in order
wire_solved = False  # becomes True when puzzle is completed

# =========================
#   GUI SETUP
# =========================

root = tk.Tk()
root.title("Wire Puzzle")
root.geometry("420x250")
root.config(bg="#121213")

title_label = tk.Label(
    root,
    text="WIRE PANEL",
    font=("Helvetica", 20, "bold"),
    bg="#121213",
    fg="white"
)
title_label.pack(pady=10)

# Hint label
hint_label = tk.Label(
    root,
    text=WIRE_HINTS[0],
    font=("Helvetica", 12),
    bg="#121213",
    fg="white",
    wraplength=380,
    justify="center"
)
hint_label.pack(pady=5)

# Frame for wire buttons
button_frame = tk.Frame(root, bg="#121213")
button_frame.pack(pady=15)


def cut_wire(color):
    global wire_step, wire_solved

    if wire_solved:
        return  # already solved, ignore extra clicks

    # Check if the clicked wire is the correct next one
    if color == WIRE_ORDER[wire_step]:
        wire_step += 1

        if wire_step == len(WIRE_ORDER):
            wire_solved = True
            hint_label.config(
                text="All wires correct! Puzzle defused.",
                fg="#00ff00"
            )
        else:
            hint_label.config(
                text=WIRE_HINTS[wire_step],
                fg="white"
            )
    else:
        # Wrong wire: reset the sequence
        wire_step = 0
        hint_label.config(
            text="Wrong wire! Sequence reset.\n\n" + WIRE_HINTS[0],
            fg="red"
        )


# Create wire buttons
for i, color in enumerate(WIRE_COLORS):
    # Map text color "GREY" to a Tkinter-friendly background "gray"
    if color == "GREY":
        bg_color = "gray"
    else:
        bg_color = color.lower()

    btn = tk.Button(
        button_frame,
        text=color,
        font=("Helvetica", 12, "bold"),
        width=8,
        height=2,
        bg=bg_color,
        fg="white" if color not in ("WHITE",) else "black",
        activebackground=bg_color,
        command=lambda c=color: cut_wire(c)
    )
    btn.grid(row=0, column=i, padx=5, pady=5)

root.mainloop()
