#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: 
#################################

# import the configs
from bomb_configs import *
# other imports
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
import os
import sys

import random
from PIL import Image, ImageTk
# global strikes counter (starts from NUM_STRIKES in bomb_configs)
strikes_left = NUM_STRIKES


#Jaeden : I got help creating the Wordle and Wires phase logic from ChatGPT, but I made sure to understand the code and comment it well.

#Random words for the Wordle to choose from
WORDLE_WORDS = [
    "SPOOK", "GHOST", "GRAVE", "SKULL", 
    "BLOOD", "CURSE", "CREEP", "SCARE", 
    "BONES", "EERIE", "FANGS", "MASKS", 
    "HAUNT", "DEVIL", "DEMON", "WITCH",
]
QUIZ_QUESTIONS = [
    {
        "prompt": "How many bits are in one byte?",
        "choices": ["4", "8", "16", "32"],
        "correct_choice": "B",     # lever B should be up
        "type": "mc",
        "code": "7"                # number you must enter on keypad after
    },
    {
        "prompt": "What is 6 × 7?",
        "choices": None,           # numeric / math question
        "type": "numeric",
        "answer_number": 42        # user types 42 on keypad
    },
    {
        "prompt": "What is the time complexity of binary search on a sorted list?",
        "choices": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "correct_choice": "C",
        "type": "mc",
        "code": "3"
    },
    {
        "prompt": "The haunted clock chimes 3 times, then 4 times, and repeats this pattern twice. How many total chimes do you hear?",
        "choices": None,
        "type": "numeric",
        "answer_number": 14
    },
    {
        "prompt": "In Python, which of these values is a boolean?",
        "choices": ["\"True\"", "1", "True", "\"False\""],
        "correct_choice": "C",
        "type": "mc",
        "code": "9"
    },
    {
        "prompt": "You are in a dark hallway. You see 2 doors on the left and 3 on the right. Each door hides 5 ghosts. How many ghosts total?",
        "choices": None,
        "type": "numeric",
        "answer_number": 25
    },
]


# the LCD display GUI
class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        try:
            # Load and set the background image
            bg_img = Image.open("haunted_house.png")

            #Force the image to fit the screen
            window.update_idletasks()

            # Resize to match the window size
            bg_img = bg_img.resize((window.winfo_screenwidth(), window.winfo_screenheight()))

            # Convert to PhotoImage
            self.bg_image = ImageTk.PhotoImage(bg_img)

            # Create a label to show the background
            self.background_label = Label(self, image=self.bg_image, borderwidth=0)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.lower(self.background_label)

        except Exception as e:
            # If the image fails to load, print an error but continue
            print("BACKGROUND FAILED:", e)
        
        # bring the GUI to the front
        self.lift()
        # make the GUI fullscreen
        window.geometry("1100x700")
        window.config(bg="black")
        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        # setup the initial "boot" GUI
        self.setupBoot()
        self.wordle_game_over = False
        self.current_minigame = "wordle"
                # hardware components from bomb_configs
        self.component_wires = component_wires
        self.component_toggles = component_toggles

        # Quiz phase state
        self.quiz_questions = QUIZ_QUESTIONS
        self.quiz_index = 0
        self.quiz_mode = None          # "mc" or "numeric"
        self.quiz_state = None         # "awaiting_answer" or "awaiting_code"
        self.quiz_keypad_buffer = ""   # for numeric and code input
        self.quiz_penalty_seconds = 15




    # sets up the LCD "boot" GUI
    def setupBoot(self):
        # set column weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        # the scrolling informative "boot" text
        self._lscroll = Label(self, bg="black", fg="white", font=("Courier New", 14), text="", justify=LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=W)
        self.pack(fill=BOTH, expand=True)

    # sets up the LCD GUI
    def setup(self):
        # destroy the boot text widget
        self._lscroll.destroy()
        
        #Mapping of T9 keys to letters
        self.t9_map = {
            "2": "ABC",
            "3": "DEF",
            "4": "GHI",
            "5": "JKL",
            "6": "MNO",
            "7": "PRS",
            "8": "TUV",
            "9": "WXY"
        }

        self.t9_state = {key: 0 for key in self.t9_map}   # rotation counters


        #Timer Label
        self._ltimer = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=0, column=0, columnspan=3, sticky="w")


        #Wordle Phase Status Label
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wordle Keypad Phase: ")
        self._lkeypad.grid(row=1, column=0, columnspan=3, sticky="w")

        #Wires Phase Status Label
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wire Combination Phase: ")
        self._lwires.grid(row=1, column=1, columnspan=3, sticky="e", padx=150)

        #Button Phase Status Label
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=2, column=0, columnspan=3, sticky="w")

        #Toggles Phase Status Label
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=2, column=1, columnspan=3, sticky="e", padx=150)

        #Strikes Left Label
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=0, column=2, sticky="e", padx=150)

        
        # -----------------------------------------
        # Beginning of Wordle Phase Methods


        #Choose a random target word for Wordle
        self.wordle_target = random.choice(WORDLE_WORDS)
        # Puts the answer for the Wordle in the terminal for easier testing
        print("DEBUG spooky Wordle answer =", self.wordle_target)

        #Allowing keyboard input for testing purposes
        # Enter key to submit row
        self.bind_all("<Return>", self.handle_return)

        # Letter typing (A–Z)
        self.bind_all("<Key>", self.wordle_keypress)


        # Create the Wordle frame
        self.game_frame = Frame(
            self,
            bg="gray20",
            width=378,   
            height=330,     
            highlightthickness=2,
            highlightbackground="#00ff00"  # green border to see it clearly
        )

        # Position the frame in the grid
        self.game_frame.grid(
            row=3,
            column=0,
            columnspan=3,  
            sticky="n",
            padx=0,
            pady=20
        )

        # Prevent frame from resizing to fit contents
        self.game_frame.grid_propagate(False)
        MAX_ATTEMPTS = 6      # 6 rows
        WORD_LENGTH = 5       # 5 columns
        FONT = ("Courier New", 24, "bold")

        # Define colors
        COLORS = {
            "empty": "black"
        }

        # Create the grid of labels for Wordle
        self.wordle_labels = []

        for row in range(MAX_ATTEMPTS):
            row_labels = []
            for col in range(WORD_LENGTH):
                lbl = Label(
                    self.game_frame,
                    text="",
                    width=3,
                    height=1,
                    font=FONT,
                    relief="solid",
                    bg=COLORS["empty"],
                    fg="white",
                    bd=2
                )
                lbl.grid(row=row, column=col, padx=6, pady=6)
                row_labels.append(lbl)

            self.wordle_labels.append(row_labels)

        # Current row and column for typing
        self.current_row = 0
        self.current_col = 0

    def addStrike(self):
        """Reduce strikes_left and update the label."""
        global strikes_left
        strikes_left -= 1
        try:
            self._lstrikes["text"] = f"Strikes left: {strikes_left}"
        except AttributeError:
            # label might not exist yet in some paths
            pass
            
    def handle_return(self, event):
        """What Enter does depends on the current minigame."""
        if self.current_minigame == "wires":
            # Submit wires pattern
            self.wires_handle_submit()
        elif self.current_minigame == "quiz":
            # Submit quiz answer or code
            self.quiz_handle_submit()
        else:
            # Default: Wordle submit
            self.wordle_submit_row()
            
    # Wordle Phase Methods
    def wordle_set_letter(self, row, col, letter):
        self.wordle_labels[row][col]["text"] = letter.upper()

    # Type a letter into the current position
    def wordle_type_letter(self, letter):
        
        # Only allow letters A–Z 
        if not letter.isalpha() or len(letter) != 1:
            return
        
        # Check bounds
        if self.current_row >= 6:
            return
        # Max 5 letters per row
        if self.current_col >= 5: 
            return

        
        # Place the letter
        self.wordle_labels[self.current_row][self.current_col]["text"] = letter.upper()
        self.current_col += 1

        # Reset T9 rotation so next letter starts fresh
        for k in self.t9_state:
            self.t9_state[k] = 0

    # Test a full word (for testing purposes)
    def wordle_test_word(self, word):
        for letter in word:
            self.wordle_type_letter(letter)

    # Backspace method
    def wordle_backspace(self):

        if self.current_col > 0:
            self.current_col -= 1
            self.wordle_labels[self.current_row][self.current_col]["text"] = ""

    # Submit the current row for checking
    def wordle_submit_row(self):
        if self.wordle_game_over:
            return

    # Read the current row's text
        row_text = "".join(self.wordle_labels[self.current_row][c]["text"] for c in range(5))
        if len(row_text) < 5:
            return

        # Evaluate the guess
        guess = row_text.upper()
        target = self.wordle_target.upper()

        # Color the tiles based on correctness
        for col in range(5):
            letter = guess[col]

            if letter == target[col]:
                self.wordle_labels[self.current_row][col]["bg"] = "#538d4e"  
            elif letter in target:
                self.wordle_labels[self.current_row][col]["bg"] = "#b59f3b"  
            else:
                self.wordle_labels[self.current_row][col]["bg"] = "#3a3a3c"  

        # Check if the guess is correct
        if guess == target:
            self.wordle_game_over = True
            self.after(700, self.wordle_win)  
            return

        # Check if out of attempts
        if self.current_row == 5:
            self.wordle_game_over = True
            self.after(700, self.wordle_lose)
            return

        # Advance to next row
        self.current_row += 1
        self.current_col = 0
        for k in self.t9_state:
            self.t9_state[k] = 0

    # Handle keypress events for Wordle
    def wordle_keypress(self, event):
        # ignore special keys
        if len(event.char) != 1:
            return

        char = event.char.upper()

        # Letter keys A–Z
        if "A" <= char <= "Z":
            self.wordle_type_letter(char)

        # Backspace key
        elif event.keysym == "BackSpace":
            self.wordle_backspace()

    # Evaluate a guess against the target word
    def wordle_check_row(self, guess, target):
        result = ["gray"] * 5
        target_list = list(target)

    # Pass 1: Mark greens
        for i in range(5):
            if guess[i] == target[i]:
                result[i] = "green"
                target_list[i] = None  # remove so yellow doesn't reuse

    # Pass 2: Mark yellows
        for i in range(5):
            if result[i] == "green":
                continue

            if guess[i] in target_list:
                result[i] = "yellow"
                target_list[target_list.index(guess[i])] = None

        return result
    
    # Wordle win handling
    def wordle_win(self):
  
        # Tell bomb this phase is defused
        self._lkeypad["text"] = "Wordle Keypad phase: DEFUSED"

        self.start_wires_phase()

    def wordle_lose(self):

        # Tell bomb this phase is failed
        self._lkeypad["text"] = "Wordle Keypad phase: FAILED"

        # If WOrdle phase is failed, add a strike
        self.addStrike()

    # Confirm letter method for T9 input
    def wordle_confirm_letter(self):
        # Only confirm if there's a letter to confirm
        if self.current_col < 5 and self.wordle_labels[self.current_row][self.current_col]["text"] != "":
            self.current_col += 1
    
        # Reset T9 rotation so next letter starts fresh
        for k in self.t9_state:
            self.t9_state[k] = 0

    # Preview letter method for T9 input
    def wordle_type_letter_preview(self, letter):
        if self.current_col < 5:
            self.wordle_labels[self.current_row][self.current_col]["text"] = letter


    #End of Wordle Phase Methods

    # -----------------------------------------

    #Beginning of Wires Phase Methods
    
    # Start the Wires Phase
    def start_wires_phase(self):
        self.current_minigame = "wires"

        # Hide the Wordle frame safely
        try:
            if hasattr(self, "game_frame") and self.game_frame:
                self.game_frame.grid_forget()
        except:
            pass

        # Create the wires frame    
        self.wires_frame = Frame(
            self,
            bg="black",
            highlightthickness=2,
            highlightbackground="#00ff00",
            width=500,
            height=400
        )
        # Position the frame in the grid
        self.wires_frame.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="n",
            padx=0,
            pady=20
        )
        # Prevent frame from resizing to fit contents
        self.wires_frame.grid_propagate(False)

        # Title text
        self.wires_text = Label(
            self.wires_frame,
            text="Wires Phase Test Frame Loaded",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 20)
        )
        #Text position
        self.wires_text.pack(pady=20)
            # PC TEST: Button to submit wires pattern
        self.wires_submit_btn = tkinter.Button(
            self.wires_frame,
            text="Submit Wires (PC)",
            bg="black",
            fg="#00ff00",
            font=("Courier New", 14),
            command=self.wires_handle_submit
       )
        self.wires_submit_btn.pack(pady=10)


        # Indicators for the 5 wires
        self.wire_indicators = []
        for i in range(5):
            box = Label(
                self.wires_frame,
                text=f"Wire {i+1}",
                fg="#00ff00",
                bg="gray20",
                width=12,
                height=2,
                relief="solid",
                bd=2,
                font=("Courier New", 14)
            )
            box.pack(pady=5)
            self.wire_indicators.append(box)

        # Internal variables
        self.wires_round_results = []
        # Start round 1
        self.wires_start_round(0)
        # Start updating
        self.update_wire_indicators()

    # Begin a specific wires round
    def wires_start_round(self, round_index):
        # Initialize round variables
        self.current_round = round_index

        #Number of attempts per round
        self.current_attempt = 1  

        # Number of correct wires for each round, round 1 = 2 wires, Round 2 = 3 wires, Round 3 = 4 wires
        difficulty_correct_counts = [2, 3, 4]

        #Number of correct wires needed this round 
        needed = difficulty_correct_counts[round_index]

        # Generate a target pattern like "10100" with EXACTLY 'needed' ones
        import random
        pattern_list = ["1"] * needed + ["0"] * (5 - needed)
        random.shuffle(pattern_list)
        self.wires_target_pattern = "".join(pattern_list)

        # Puts the answer for the Wires in the terminal for easier testing
        print(f"[DEBUG] Starting Round {round_index+1}, target = {self.wires_target_pattern}")

        # Update the text on screen
        self.wires_text.config(
            text=f"Round {round_index+1}/3\n\n"
                f"The house whispers...\n"
                f"\"\"\"{needed} conduits carry the hidden current...\"\"\"\n\n"
                f"Attempt {self.current_attempt}/2"
        )

    # Handle submission of wires pattern
    def wires_handle_submit(self):
        pattern = self.read_wires_pattern()

        # Puts the user submission for the Wires in the terminal and compares it to the target for easier testing
        print(f"[DEBUG] Player submitted {pattern}, target = {self.wires_target_pattern}")

        # Check correctness
        if pattern == self.wires_target_pattern:
            self.wires_round_results.append(True)
            self.wires_text.config(text="Correct alignment!\nThe energy surges through the walls...")
            self.after(1500, self.wires_next_round)
            return

        # Incorrect submission, but user gets another try
        if self.current_attempt == 1:
            self.current_attempt = 2
            self.wires_text.config(
                text=f"Incorrect...\nThe current sputters.\n\n"
                    f"Attempt {self.current_attempt}/2"
            )
            return
        # Second incorrect submission, check if this was the last round

        # Checks if the user failed this round
        self.wires_round_results.append(False)
        self.wires_text.config(text="The wires fall silent...\nThis round is lost.")
        self.after(1500, self.wires_next_round)

    # Advance to next round or end the wires phase
    def wires_next_round(self):
        if self.current_round == 2:
            # All 3 rounds complete
            wins = sum(self.wires_round_results)

            # Use finish_wires_phase() which hides UI AND moves to next phase
            self.finish_wires_phase()
            return

        # Continue to next round
        self.wires_start_round(self.current_round + 1)

    # Update the wire indicators based on current state
    def update_wire_indicators(self):

        # Read the current wires pattern
        pattern = self.read_wires_pattern()  

        # Update the indicators
        for i in range(5):
            bit = pattern[i]
            if bit == "1":
                self.wire_indicators[i].config(bg="green4")
            else:
                self.wire_indicators[i].config(bg="gray20")
        #Update the gui wire indicators every 100ms
        self.after(100, self.update_wire_indicators)

    # Read the current wires pattern from GPIO pins
    def read_wires_pattern(self):
        if RPi:
            bits = []
            for pin in self.component_wires:
                plugged = (pin.value == True)
                bits.append("1" if plugged else "0")
            return "".join(bits)
        else:
            return "00000"

    # Finish the wires phase and show summary
    def finish_wires_phase(self):
        total_successes = sum(self.wires_round_results)

        # Clear the wires frame UI
        try:
            self.wires_frame.grid_forget()
        except:
            pass

        # Show summary screen
        self.wires_summary = Frame(
            self,
            bg="black",
            highlightthickness=2,
            highlightbackground="#00ff00"
        )
        self.wires_summary.grid(row=6, column=1, columnspan=3, sticky="w", padx=20, pady=20)

        # Title
        Label(
            self.wires_summary,
            text="Wires Phase Complete",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 22, "bold")
        ).pack(pady=10)

        # Detailed results
        Label(
            self.wires_summary,
            text=f"Correct rounds: {total_successes}/3",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 18)
        ).pack(pady=10)

        # Determine pass/fail
        if total_successes >= 2:
            Label(
                self.wires_summary,
                text="Result: DEFUSED",
                fg="green",
                bg="black",
                font=("Courier New", 20, "bold")
            ).pack(pady=10)

            # Proceed to button phase after delay
            self.after(2000, self.start_button_phase)

        else:
            #If the user failed the wires phase
            Label(
                self.wires_summary,
                text="Result: FAILED",
                fg="red",
                bg="black",
                font=("Courier New", 20, "bold")
            ).pack(pady=10)

            # Add a strike for failing the wires phase
            global strikes_left
            strikes_left -= 1

            #Start button phase after delay
            self.after(2000, self.start_button_phase)

    #End of Wires Phase Methods

    # -----------------------------------------

    #Beginning of Button Phase Methods
    def start_button_phase(self):
        self.current_minigame = "button_ritual"

        # Hide wires frame (if it exists)
        try:
            if hasattr(self, "wires_frame") and self.wires_frame:
                self.wires_frame.grid_forget()
        except:
            pass

        try:
            if hasattr(self, "wires_summary") and self.wires_summary:
                self.wires_summary.grid_forget()
        except:
            pass

        # Create ritual frame
        self.ritual_frame = Frame(
            self,
            bg="black",
            highlightthickness=2,
            highlightbackground="#00ff00",
            width=500,
            height=400
        )
        self.ritual_frame.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="n",
            padx=0,
            pady=20
        )
        self.ritual_frame.grid_propagate(False)

        # Title text
        Label(
            self.ritual_frame,
            text="RITUAL OF THE SIGILS",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 24, "bold")
        ).pack(pady=10)

        # Story text
        self.ritual_text = Label(
            self.ritual_frame,
            text="The sigils flicker with spectral energy...\nWatch closely.",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 16)
        )
        self.ritual_text.pack(pady=5)

        # Space for the color sequence display
        self.ritual_sequence_label = Label(
            self.ritual_frame,
            text="(sequence will appear here)",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 20, "bold")
        )
        self.ritual_sequence_label.pack(pady=20)

        # Space for user input feedback
        self.ritual_input_label = Label(
            self.ritual_frame,
            text="Awaiting your input...",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 18)
        )
        self.ritual_input_label.pack(pady=10)

        # Initialize internal variables for the ritual
        self.ritual_round = 0
        self.ritual_attempts = 2
        self.ritual_sequence = []
        self.ritual_user_input = []
        self.after(800, self.ritual_begin_round)

    def ritual_begin_round(self):
        """Begin a new ritual round with a generated sequence."""

        # Increase sequence length each round
        lengths = [2, 3, 4]   # Round 1 → 2 colors, Round 2 → 3, Round 3 → 4
        seq_length = lengths[self.ritual_round]

        colors = ["RED", "GREEN", "BLUE"]
        self.ritual_sequence = [choice(colors) for _ in range(seq_length)]

        self.ritual_text.config(
            text=f"Ritual Round {self.ritual_round + 1}\nFocus on the sigils..."
        )

        # Reset user input
        self.ritual_user_input = []
        self.ritual_input_label.config(text="Awaiting your input...")

        # Begin sequence display
        self.after(1000, lambda: self.ritual_display_sequence(0))


        # Placeholder until next step
        print("[DEBUG] Ritual phase frame loaded.")

    def ritual_display_sequence(self, index):
        """Shows color sequence one at a time."""
        if index >= len(self.ritual_sequence):
            # Done showing sequence
            self.ritual_sequence_label.config(text="Now repeat the sigils.")
            return

        color = self.ritual_sequence[index]

        # Display the color text on screen
        self.ritual_sequence_label.config(text=color)

        # Flash for 700ms then blank
        self.after(700, lambda: self.ritual_sequence_label.config(text=""))
        self.after(1000, lambda: self.ritual_display_sequence(index + 1))
        # -------------------------------
    # QUIZ PHASE (multiple choice + math)
    # -------------------------------
        if self.ritual_round == 2:
        # Finished all 3 ritual rounds
            self.after(1500, self.start_quiz_phase)

    def start_quiz_phase(self):
        """Begin the spooky quiz phase."""
        self.current_minigame = "quiz"

        # Hide any previous phase frames if they exist
        for attr in ("game_frame", "wires_frame", "wires_summary", "ritual_frame"):
            try:
                frame = getattr(self, attr, None)
                if frame is not None:
                    frame.grid_forget()
            except:
                pass

        # Create quiz frame
        self.quiz_frame = Frame(
            self,
            bg="black",
            highlightthickness=2,
            highlightbackground="#00ff00",
            width=500,
            height=400
        )
        self.quiz_frame.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="n",
            padx=0,
            pady=20
        )
        self.quiz_frame.grid_propagate(False)

        # Title
        Label(
            self.quiz_frame,
            text="FINAL QUIZ OF THE HAUNTED TERMINAL",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 20, "bold")
        ).pack(pady=10)

        # Question label
        self.quiz_question_label = Label(
            self.quiz_frame,
            text="",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 16),
            wraplength=480,
            justify="left"
        )
        self.quiz_question_label.pack(pady=10)

        # Choices label (for MC questions)
        self.quiz_choices_label = Label(
            self.quiz_frame,
            text="",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 14),
            justify="left"
        )
        self.quiz_choices_label.pack(pady=5)

        # Instructions for lever mapping
        self.quiz_lever_help = Label(
            self.quiz_frame,
            text="Levers: A=1000, B=0100, C=0010, D=0001 (left to right)\n"
                 "Set one pattern, then press # to lock in.",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 12),
            justify="left"
        )
        self.quiz_lever_help.pack(pady=5)

        # Keypad entry display (for numeric answers & codes)
        self.quiz_entry_label = Label(
            self.quiz_frame,
            text="Keypad: ",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 16)
        )
        self.quiz_entry_label.pack(pady=5)

        # Status / feedback
        self.quiz_status_label = Label(
            self.quiz_frame,
            text="Answer the questions to escape...",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 14)
        )
        self.quiz_status_label.pack(pady=10)

        # Reset state and show first question
        self.quiz_index = 0
        self.quiz_keypad_buffer = ""
        self.load_quiz_question()

    def load_quiz_question(self):
        """Display the current question and reset state."""
        if self.quiz_index >= len(self.quiz_questions):
            # All questions done – you win
            self.quiz_status_label.config(text="You answered all questions. The house releases you...")
            # You could call self.conclusion(success=True) here if you want:
            # self.after(2000, lambda: self.conclusion(success=True))
            return

        q = self.quiz_questions[self.quiz_index]
        self.quiz_mode = q["type"]
        self.quiz_state = "awaiting_answer"
        self.quiz_keypad_buffer = ""
        self.quiz_entry_label.config(text="Keypad: ")

        self.quiz_question_label.config(text=f"Q{self.quiz_index + 1}: {q['prompt']}")

        if q["type"] == "mc":
            # Show choices A–D
            choices_text = []
            letters = ["A", "B", "C", "D"]
            for i, choice in enumerate(q["choices"]):
                choices_text.append(f"{letters[i]}) {choice}")
            self.quiz_choices_label.config(text="\n".join(choices_text))
            self.quiz_lever_help.config(
                text="Levers: A=1000, B=0100, C=0010, D=0001 (left to right)\n"
                     "Set one pattern, then press # to lock in."
            )
        else:
            # Numeric question – no choices
            self.quiz_choices_label.config(text="(Type your answer on the keypad, then press #.)")
            self.quiz_lever_help.config(
                text="Levers not used for this question.\n"
                     "Use keypad digits, * to clear, # to submit."
            )

        self.quiz_status_label.config(text="Answer carefully... a wrong answer will anger the house.")

    def quiz_type_digit(self, digit):
        """Append a digit to the keypad buffer for numeric answers / codes."""
        if self.current_minigame != "quiz":
            return
        if len(self.quiz_keypad_buffer) >= 8:
            return
        self.quiz_keypad_buffer += digit
        self.quiz_entry_label.config(text=f"Keypad: {self.quiz_keypad_buffer}")

    def quiz_backspace(self):
        """Clear the keypad buffer (like reset)."""
        if self.current_minigame != "quiz":
            return
        self.quiz_keypad_buffer = ""
        self.quiz_entry_label.config(text="Keypad: ")

    def read_lever_choice(self):
        """
        Read the toggle levers and map to A/B/C/D.
        We assume 4 toggle pins in self.component_toggles (left → right).
        Pattern mapping:
            1000 -> A
            0100 -> B
            0010 -> C
            0001 -> D
        """
        if not hasattr(self, "component_toggles"):
            # No hardware attached; you can later simulate if needed
            return None

        if RPi:
            bits = []
            for pin in self.component_toggles:
                up = (pin.value is True)
                bits.append("1" if up else "0")
            pattern = "".join(bits)
        else:
            # On non-RPi systems, default no choice
            pattern = "0000"

        mapping = {
            "1000": "A",
            "0100": "B",
            "0010": "C",
            "0001": "D"
        }
        return mapping.get(pattern, None)

    def quiz_handle_submit(self):
        """Real quiz logic for # submit button."""
        if self.current_minigame != "quiz":
            return

        q = self.quiz_questions[self.quiz_index]

        # --------------------------
        # MULTIPLE CHOICE QUESTIONS
        # --------------------------
        if q["type"] == "mc":

        # Step 1 — if waiting for lever input
            if self.quiz_state == "awaiting_answer":
                lever_choice = self.read_lever_choice()

                if lever_choice is None:
                    self.quiz_status_label.config(text="No lever selected!")
                    return

                if lever_choice != q["correct_choice"]:
                    self.quiz_wrong_answer()
                    return

            # Lever was correct → now require keypad code
                self.quiz_state = "awaiting_code"
                self.quiz_status_label.config(text="Correct lever! Enter the code then press #.")
                return

        # Step 2 — waiting for keypad code
            elif self.quiz_state == "awaiting_code":
                if self.quiz_keypad_buffer == q["code"]:
                    # MC question fully correct
                    self.quiz_index += 1
                    self.quiz_status_label.config(text="Correct! Proceeding...")
                    self.after(300, self.load_quiz_question)
                else:
                    self.quiz_wrong_answer()
                return

    # --------------------------
    # NUMERIC QUESTIONS
    # --------------------------
        elif q["type"] == "numeric":
            if not self.quiz_keypad_buffer.isdigit():
                self.quiz_status_label.config(text="Enter a number!")
                return

            player_num = int(self.quiz_keypad_buffer)

            if player_num == q["answer_number"]:
                self.quiz_index += 1
                self.quiz_status_label.config(text="Correct! Next question...")
                self.after(300, self.load_quiz_question)
            else:
                self.quiz_wrong_answer()
            return


        
    def quiz_wrong_answer(self):
        """Apply time penalty + jump scare when the player is wrong."""
        self.quiz_status_label.config(text="Wrong! The house SCREAMS at you!")
        self.quiz_keypad_buffer = ""
        self.quiz_entry_label.config(text="Keypad: ")
        # time penalty
        self.quiz_time_penalty(self.quiz_penalty_seconds)
        # spooky popup
        self.show_jumpscare()

    def quiz_time_penalty(self, seconds):
        """Reduce the bomb timer when you miss a question."""
        if self._timer is not None:
            try:
                self._timer._value = max(0, self._timer._value - seconds)
            except Exception as e:
                print("Could not reduce timer:", e)

    def show_jumpscare(self):
        """Quick scary popup; tries to use jumpscare.png if available."""
        try:
            js = Toplevel(self)
            js.configure(bg="black")
            js.overrideredirect(True)
            js.attributes("-topmost", True)

            parent = self.winfo_toplevel()
            parent.update_idletasks()
            # match main window size
            try:
                w = parent.winfo_width()
                h = parent.winfo_height()
                x = parent.winfo_rootx()
                y = parent.winfo_rooty()
                js.geometry(f"{w}x{h}+{x}+{y}")
            except:
                js.geometry("1100x700")

            # Try to load scary image
            try:
                img = Image.open("jumpscare.png")
                img = img.resize((w, h))
                self.jumpscare_image = ImageTk.PhotoImage(img)
                Label(js, image=self.jumpscare_image, bg="black").pack(fill="both", expand=True)
            except Exception as e:
                print("JUMPSCARE IMAGE FAILED:", e)
                Label(
                    js,
                    text="BOO!",
                    fg="red",
                    bg="black",
                    font=("Courier New", 80, "bold")
                ).pack(expand=True, fill="both")

            # Auto-close after ~1.2 seconds
            js.after(1200, js.destroy)
        except Exception as e:
            print("Error showing jumpscare:", e)

    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button

    def setKeypad(self, keypad):
        self._keypad = keypad

    # pauses the timer
    def pause(self):
        if (RPi):
            self._timer.pause()

    # setup the conclusion GUI (explosion/defusion)
    def conclusion(self, success=False):
        # destroy/clear widgets that are no longer needed
        self._lscroll["text"] = ""
        self._ltimer.destroy()
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()
        if (SHOW_BUTTONS):
            self._bpause.destroy()
            self._bquit.destroy()

        # reconfigure the GUI
        # the retry button
        self._bretry = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Retry", anchor=CENTER, command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)
        # the quit button
        self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
        self._bquit.grid(row=1, column=1, pady=40)

    # re-attempts the bomb (after an explosion or a successful defusion)
    def retry(self):
        # re-launch the program (and exit this one)
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    # quits the GUI, resetting some components
    def quit(self):
        if (RPi):
            # turn off the 7-segment display
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            # turn off the pushbutton's LED
            for pin in self._button._rgb:
                pin.value = True
        # exit the application
        exit(0)

# template (superclass) for various bomb components/phases
class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        # phases have an electronic component (which usually represents the GPIO pins)
        self._component = component
        # phases have a target value (e.g., a specific combination on the keypad, the proper jumper wires to "cut", etc)
        self._target = target
        # phases can be successfully defused
        self._defused = False
        # phases can be failed (which result in a strike)
        self._failed = False
        # phases have a value (e.g., a pushbutton can be True/Pressed or False/Released, several jumper wires can be "cut"/False, etc)
        self._value = None
        # phase threads are either running or not
        self._running = False

# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # the default value is the specified initial value
        self._value = initial_value
        # is the timer paused?
        self._paused = False
        # initialize the timer's minutes/seconds representation
        self._min = ""
        self._sec = ""
        # by default, each tick is 1 second
        self._interval = 1

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            if (not self._paused):
                # update the timer and display its value on the 7-segment display
                self._update()
                self._component.print(str(self))
                # wait 1s (default) and continue
                sleep(self._interval)
                # the timer has expired -> phase failed (explode)
                if (self._value == 0):
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)

    # updates the timer (only internally called)
    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    # pauses and unpauses the timer
    def pause(self):
        # toggle the paused state
        self._paused = not self._paused
        # blink the 7-segment display when paused
        self._component.blink_rate = (2 if self._paused else 0)

    # returns the timer as a string (mm:ss)
    def __str__(self):
        return f"{self._min}:{self._sec}"

# the keypad phase
class Keypad(PhaseThread):
    def __init__(self, component, target, gui, name="Keypad"):
        super().__init__(name, component, target)
        # the default value is an empty string
        self.gui = gui
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while self._running:
            if self._component.pressed_keys:
                try:
                    key = str(self._component.pressed_keys[0])
                except:
                    key = ""
                while self._component.pressed_keys:
                    sleep(0.1)
            
                            # =============== QUIZ MODE ===============
                if getattr(self.gui, "current_minigame", None) == "quiz":
                    if key in "0123456789":
                        self.gui.quiz_type_digit(key)
                    elif key == "*":
                        self.gui.quiz_backspace()
                    elif key == "#":
                        self.gui.quiz_handle_submit()
                    sleep(0.1)
                    continue

                # =============== WIRES MODE ===============
                if getattr(self.gui, "current_minigame", None) == "wires":
                    if key == "#":
                        try:
                            self.gui.wires_handle_submit()
                        except Exception as e:
                            print("Error in wires # handling:", e)
                    sleep(0.1)
                    continue

                # =============== WORDLE MODE (T9) ===============
                if key in self.gui.t9_map:
                    letters = self.gui.t9_map[key]
                    idx = self.gui.t9_state[key]
                    letter = letters[idx]
                    self.gui.wordle_type_letter_preview(letter)
                    self.gui.t9_state[key] = (idx + 1) % len(letters)

                elif key == "1":
                    self.gui.wordle_confirm_letter()

                elif key == "*":
                    self.gui.wordle_backspace()

                elif key == "#":
                    try:
                        self.gui.wordle_submit_row()
                    except Exception as e:
                        print("Error in # handling:", e)

            sleep(0.1)


    # returns the keypad combination as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value

# the jumper wires phase
class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)

    # runs the thread
    def run(self):
        # TODO
        pass

    # returns the jumper wires state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            # TODO
            pass

# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        # the default value is False/Released
        self._value = False
        # has the pushbutton been pressed?
        self._pressed = False
        # we need the pushbutton's RGB pins to set its color
        self._rgb = component_rgb
        # the pushbutton's randomly selected LED color
        self._color = color
        # we need to know about the timer (7-segment display) to be able to determine correct pushbutton releases in some cases
        self._timer = timer

    # runs the thread
    def run(self):
        self._running = True
        # set the RGB LED color
        self._rgb[0].value = False if self._color == "R" else True
        self._rgb[1].value = False if self._color == "G" else True
        self._rgb[2].value = False if self._color == "B" else True
        while (self._running):
            # get the pushbutton's state
            self._value = self._component.value
            # it is pressed
            if (self._value):
                # note it
                self._pressed = True
            # it is released
            else:
                # was it previously pressed?
                if (self._pressed):
                    # check the release parameters
                    # for R, nothing else is needed
                    # for G or B, a specific digit must be in the timer (sec) when released
                    if (not self._target or self._target in self._timer._sec):
                        self._defused = True
                    else:
                        self._failed = True
                    # note that the pushbutton was released
                    self._pressed = False
            sleep(0.1)

    # returns the pushbutton's state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return str("Pressed" if self._value else "Released")

# the toggle switches phase
class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)

    # runs the thread
    def run(self):
        # TODO
        pass

    # returns the toggle switches state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            # TODO
            pass
if __name__ == "__main__":
    print("Starting spooky bomb GUI...")  # debug print so we know this runs

    # Create the main Tkinter window
    root = Tk()
    root.title("Spooky Bomb")

    # Create the LCD GUI
    lcd = Lcd(root)

    # Build the LCD interface (timer label, phase labels, Wordle grid, etc.)
    lcd.setup()
    
    lcd.start_quiz_phase()

    # Start Tkinter event loop (this actually opens the window)
    root.mainloop()
