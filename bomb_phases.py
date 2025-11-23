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
        window.attributes("-fullscreen", True)
        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        # setup the initial "boot" GUI
        self.setupBoot()
        self.wordle_game_over = False


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

    


    # Build guess string
        guess = "".join(self.wordle_labels[self.current_row][i]["text"] for i in range(5))

    # Temporary target word — later we’ll link this to the bomb logic!
        target = "APPLE"

    # Evaluate guess
        colors = self.wordle_check_row(guess, target)

    # Apply colors to labels
        for i in range(5):
            if colors[i] == "green":
                self.wordle_labels[self.current_row][i].config(bg="#538d4e")   # green
            elif colors[i] == "yellow":
                self.wordle_labels[self.current_row][i].config(bg="#b59f3b")   # yellow
            else:
                self.wordle_labels[self.current_row][i].config(bg="#3a3a3c")   # gray

    # After coloring, move to next row
        self.current_row += 1
        self.current_col = 0

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
        self.game_frame.destroy()

        # Tell bomb this phase is defused
        self._lkeypad["text"] = "Wordle Keypad phase: DEFUSED"

    # TODO: call the next bomb phase setup
    # example:
    # self.start_wires_phase()

    def wordle_lose(self):
    # Remove Wordle frame
        self.game_frame.destroy()

        self._lkeypad["text"] = "Wordle Keypad phase: FAILED"

    # apply a strike
    # (example, depends on your strike system)
    # self.addStrike()

    # continue to next phase or trigger explosion

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


    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button

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
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        # the default value is an empty string
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            # process keys when keypad key(s) are pressed
            if (self._component.pressed_keys):
                # debounce
                while (self._component.pressed_keys):
                    try:
                        # just grab the first key pressed if more than one were pressed
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                # If the key is ENTER (#), submit the Wordle row
                if str(key) == "#":
                    # call GUI's submit method safely
                    gui.wordle_submit_row()
                    continue

                # log the key
                if str(key) in gui.t9_map:
                    # cycle through the letters
                    letters = gui.t9_map[str(key)]
                    idx = gui.t9_state[str(key)]
                    letter = letters[idx]

                    gui.wordle_type_letter_preview(letter)

                    # rotate for next press
                    gui.t9_state[str(key)] = (idx + 1) % len(letters)

                    # type the letter onto the Wordle board
                    gui.wordle_type_letter(letter)

                elif str(key) == "#":
                    gui.wordle_submit_row()

                elif str(key) == "*":
                    gui.wordle_backspace()
                
                elif str(key) == "1":
                    # CONFIRM the current letter and move to next column
                    gui.wordle_confirm_letter()


                # the combination is correct -> phase defused
                
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

