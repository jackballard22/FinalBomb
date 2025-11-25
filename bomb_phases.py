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

WORDLE_WORDS = [
    "SPOOK", "GHOST", "GRAVE", "SKULL", 
    "BLOOD", "CURSE", "CREEP", "SCARE", 
    "BONES", "EERIE", "FANGS", "MASKS", 
    "HAUNT", "DEVIL", "DEMON", "WITCH",
]



#########
# classes
#########
# the LCD display GUI
class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        # make the GUI fullscreen
        window.geometry("1100x700")
        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        # setup the initial "boot" GUI
        self.setupBoot()
        self.wordle_game_over = False
        self.current_minigame = "wordle"



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


        # the timer
        self._ltimer = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=W)
        # the keypad passphrase
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wordle Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        # the jumper wires status
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        # the pushbutton status
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        # the toggle switches status
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        # the strikes left
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)
        if (SHOW_BUTTONS):
            # the pause button (pauses the timer)
            self._bpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Pause", anchor=CENTER, command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            # the quit button
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

        self.wordle_target = random.choice(WORDLE_WORDS)
        print("DEBUG spooky Wordle answer =", self.wordle_target)

        # allow Enter key on real keyboard
        self.bind_all("<Return>", lambda event: self.wordle_submit_row())
        # Letter typing (A–Z)
        self.bind_all("<Key>", self.wordle_keypress)


        # =====================================================
        # MINIGAME FRAME (bottom-left)
        # =====================================================

        self.game_frame = Frame(
            self,
            bg="gray20",
            width=470,      # adjust size if needed
            height=720,     # adjust size if needed
            highlightthickness=2,
            highlightbackground="#00ff00"  # green border to see it clearly
        )

        # Put it at the bottom-left
        self.game_frame.grid(
            row=6,
            column=0,
            columnspan=2,   # gives you more horizontal room
            sticky="nw",
            padx=20,
            pady=20
        )

        # Prevent frame from shrinking to fit contents (important)
        self.game_frame.grid_propagate(False)
        MAX_ATTEMPTS = 6      # 6 rows
        WORD_LENGTH = 5       # 5 columns
        FONT = ("Courier New", 24, "bold")

        COLORS = {
            "empty": "black"
        }

        # store a reference so later we can update tiles
        self.wordle_labels = []

        for row in range(MAX_ATTEMPTS):
            row_labels = []
            for col in range(WORD_LENGTH):
                lbl = Label(
                    self.game_frame,
                    text="",
                    width=4,
                    height=2,
                    font=FONT,
                    relief="solid",
                    bg=COLORS["empty"],
                    fg="white",
                    bd=2
                )
                lbl.grid(row=row, column=col, padx=6, pady=6)
                row_labels.append(lbl)

            self.wordle_labels.append(row_labels)
        
        # Wordle typing state
        self.current_row = 0
        self.current_col = 0




    def wordle_set_letter(self, row, col, letter):
        self.wordle_labels[row][col]["text"] = letter.upper()

    def wordle_type_letter(self, letter):
        
        # Only allow letters A–Z (optional safety check)
        if not letter.isalpha() or len(letter) != 1:
            return
        
        # If row is full, do nothing
        if self.current_row >= 6:
            return
        
        if self.current_col >= 5:  # MAX_ATTEMPTS
            return

        
        # Place the letter
        self.wordle_labels[self.current_row][self.current_col]["text"] = letter.upper()
        self.current_col += 1
        
        # If the row is now full, advance to the next row
        #if self.current_col == 5:
            #self.current_row += 1
            #self.current_col = 0
        for k in self.t9_state:
            self.t9_state[k] = 0


    def wordle_test_word(self, word):
        for letter in word:
            self.wordle_type_letter(letter)

    def wordle_backspace(self):

        if self.current_col > 0:
            self.current_col -= 1
            self.wordle_labels[self.current_row][self.current_col]["text"] = ""

    def wordle_submit_row(self):
        if self.wordle_game_over:
            return

    # Must have exactly 5 letters
        row_text = "".join(self.wordle_labels[self.current_row][c]["text"] for c in range(5))
        if len(row_text) < 5:
            return

        guess = row_text.upper()
        target = self.wordle_target.upper()

        for col in range(5):
            letter = guess[col]

            if letter == target[col]:
                self.wordle_labels[self.current_row][col]["bg"] = "#538d4e"  
            elif letter in target:
                self.wordle_labels[self.current_row][col]["bg"] = "#b59f3b"  
            else:
                self.wordle_labels[self.current_row][col]["bg"] = "#3a3a3c"  

        # Check for win
        if guess == target:
            self.wordle_game_over = True
            self.after(700, self.wordle_win)  # delay for color to show
            return

        #If not a win check if its the last row
        if self.current_row == 5:
            self.wordle_game_over = True
            self.after(700, self.wordle_lose)
            return

        # Otherwise go to next row
        self.current_row += 1
        self.current_col = 0
        for k in self.t9_state:
            self.t9_state[k] = 0

    def wordle_keypress(self, event):
        # ignore special keys
        if len(event.char) != 1:
            return

        char = event.char.upper()

        # A–Z letters → type them
        if "A" <= char <= "Z":
            self.wordle_type_letter(char)

    # Backspace → delete
        elif event.keysym == "BackSpace":
            self.wordle_backspace()

    # Enter key already handled separately
    def wordle_check_row(self, guess, target):
        """
        Returns a list of 5 color results for this guess.
        'green'  = correct letter, correct position
        'yellow' = correct letter, wrong position
        'gray'   = not in the word at all
        """

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
    def wordle_win(self):
        # Remove Wordle frame

        # Tell bomb this phase is defused
        self._lkeypad["text"] = "Wordle Keypad phase: DEFUSED"

    # TODO: call the next bomb phase setup
    # example:
        self.start_wires_phase()

    def wordle_lose(self):
    # Remove Wordle frame

        self._lkeypad["text"] = "Wordle Keypad phase: FAILED"

    # apply a strike
    # (example, depends on your strike system)
        self.addStrike()


    def wordle_confirm_letter(self):
    # If the tile already has a letter, advance
        if self.current_col < 5 and self.wordle_labels[self.current_row][self.current_col]["text"] != "":
            self.current_col += 1
    
    # Reset T9 rotation so next letter starts fresh
        for k in self.t9_state:
            self.t9_state[k] = 0

    def wordle_type_letter_preview(self, letter):
        if self.current_col < 5:
            self.wordle_labels[self.current_row][self.current_col]["text"] = letter

    ######################################
    # Wires Phase Initialization
    ######################################

    def start_wires_phase(self):
        self.current_minigame = "wires"

        # Hide the Wordle frame safely
        try:
            if hasattr(self, "game_frame") and self.game_frame:
                self.game_frame.grid_forget()
        except:
            pass

        self.wires_frame = Frame(
            self,
            bg="black",
            highlightthickness=2,
            highlightbackground="#00ff00",
            width=500,
            height=400
        )
        self.wires_frame.grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w",
            padx=20,
            pady=20
        )
        self.wires_frame.grid_propagate(False)

        # label
        self.wires_text = Label(
            self.wires_frame,
            text="Wires Phase Test Frame Loaded",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 20)
        )
        self.wires_text.pack(pady=20)

        # indicators
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

        self.wires_round_results = []
        self.wires_start_round(0)
        # Start updating
        self.update_wire_indicators()

    # -----------------------------------------
# Wires Rounds System (3 rounds, increasing difficulty)
# -----------------------------------------

    def wires_start_round(self, round_index):
        """Begin a specific wires round."""
        self.current_round = round_index
        self.current_attempt = 1   # player gets 2 attempts per round

        # Number of correct wires for each round
        difficulty_correct_counts = [2, 3, 4]    # Round 1 → 2 wires, Round 2 → 3 wires, Round 3 → 4 wires
        needed = difficulty_correct_counts[round_index]

        # Generate a target pattern like "10100" with EXACTLY 'needed' ones
        import random
        pattern_list = ["1"] * needed + ["0"] * (5 - needed)
        random.shuffle(pattern_list)
        self.wires_target_pattern = "".join(pattern_list)

        # Debug print so we can test before we go live
        print(f"[DEBUG] Starting Round {round_index+1}, target = {self.wires_target_pattern}")

        # Update the text on screen
        self.wires_text.config(
            text=f"Round {round_index+1}/3\n\n"
                f"The house whispers...\n"
                f"\"\"\"{needed} conduits carry the hidden current...\"\"\"\n\n"
                f"Attempt {self.current_attempt}/2"
        )


    def wires_handle_submit(self):
        """Called when # is pressed to lock in the player's guess."""
        pattern = self.read_wires_pattern()

        print(f"[DEBUG] Player submitted {pattern}, target = {self.wires_target_pattern}")

        # Correct!
        if pattern == self.wires_target_pattern:
            self.wires_round_results.append(True)
            self.wires_text.config(text="Correct alignment!\nThe energy surges through the walls...")
            self.after(1500, self.wires_next_round)
            return

        # Wrong — but attempt 1
        if self.current_attempt == 1:
            self.current_attempt = 2
            self.wires_text.config(
                text=f"Incorrect...\nThe current sputters.\n\n"
                    f"Attempt {self.current_attempt}/2"
            )
            return
        if round_number == 2:   # round 0, 1, 2 = 3 rounds
            self.finish_wires_phase()

        # Wrong again — fail the round
        self.wires_round_results.append(False)
        self.wires_text.config(text="The wires fall silent...\nThis round is lost.")
        self.after(1500, self.wires_next_round)


    def wires_next_round(self):
        """Advance to next round or end the puzzle."""
        if self.current_round == 2:  
            # All 3 rounds complete
            wins = sum(self.wires_round_results)
            if wins >= 2:
                self.wires_text.config(text="You restored power!\nThe house awakens...")
                # TODO → call next bomb phase here
            else:
                self.wires_text.config(text="The power collapses...\nThe spirits grow restless.")
                # TODO → strike or fail state
            return

        # Continue to next round
        self.wires_start_round(self.current_round + 1)

    def update_wire_indicators(self):

        pattern = self.read_wires_pattern()  # returns "10100"

        for i in range(5):
            bit = pattern[i]
            if bit == "1":
                self.wire_indicators[i].config(bg="green4")
            else:
                self.wire_indicators[i].config(bg="gray20")
        
        self.after(100, self.update_wire_indicators)


    def read_wires_pattern(self):
        if RPi:
            bits = []
            for pin in self.component_wires:
                plugged = (pin.value == True)
                bits.append("1" if plugged else "0")
            return "".join(bits)
        else:
            return "00000"


    def finish_wires_phase(self):
        total_successes = sum(self.wires_round_results)

        # Clear the wires frame UI
        try:
            self.wires_frame.grid_forget()
        except:
            pass

        # Show summary screen
        summary = Frame(
            self,
            bg="black",
            highlightthickness=2,
            highlightbackground="#00ff00"
        )
        summary.grid(row=6, column=0, columnspan=3, sticky="w", padx=20, pady=20)

        # Title
        Label(
            summary,
            text="Wires Phase Complete",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 22, "bold")
        ).pack(pady=10)

        # Detailed results
        Label(
            summary,
            text=f"Correct rounds: {total_successes}/3",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 18)
        ).pack(pady=10)

        # Determine pass/fail
        if total_successes >= 2:
            Label(
                summary,
                text="Result: DEFUSED",
                fg="green",
                bg="black",
                font=("Courier New", 20, "bold")
            ).pack(pady=10)

            # ➜ START NEXT PHASE HERE
            self.after(2000, self.start_button_phase)

        else:
            Label(
                summary,
                text="Result: FAILED",
                fg="red",
                bg="black",
                font=("Courier New", 20, "bold")
            ).pack(pady=10)

            # strike the bomb
            global strikes_left
            strikes_left -= 1

            # ➜ Continue to button phase anyway
            self.after(2000, self.start_button_phase)

    def start_button_phase(self):
        print("[DEBUG] Starting button phase (placeholder)")
        # TEMPORARY placeholder frame
        frame = Frame(self, bg="black")
        frame.grid(row=6, column=0, columnspan=3, sticky="w", padx=20, pady=20)

        Label(
            frame,
            text="Button Phase Starting...\n(placeholder screen)",
            fg="#00ff00",
            bg="black",
            font=("Courier New", 22)
        ).pack(pady=30)

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
        self._bquit.grid(row=1, column=2, pady=40)

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

            # wait until released (debounce)
                while self._component.pressed_keys:
                    sleep(0.1)

            # ======= T9 LETTER KEYS (2–9) =======
                if key in self.gui.t9_map:
                    letters = self.gui.t9_map[key]
                    idx = self.gui.t9_state[key]
                    letter = letters[idx]

                # PREVIEW THE LETTER ON WORDLE TILE
                    self.gui.wordle_type_letter_preview(letter)

                # rotate for next press
                    self.gui.t9_state[key] = (idx + 1) % len(letters)

            # ======= CONFIRM LETTER (1) =======
                elif key == "1":
                    self.gui.wordle_confirm_letter()

            # ======= BACKSPACE (*) =======
                elif key == "*":
                    self.gui.wordle_backspace()

            # ======= ENTER (#) =======
                elif str(key) == "#":
                    try:
                        if self.gui.current_minigame == "wires":
                            self.gui.wires_handle_submit()
                        else:
                            self.gui.wordle_submit_row()
                    except Exception as e:
                        print("Error in # handling:", e)
                    continue


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

