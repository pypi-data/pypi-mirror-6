"""
What's My Word
"""

import random
import string
import Tkinter as Tk

import __init__ as info
from pkg_resources import resource_filename


class Game(Tk.Frame):
    "The entire game."

    def __init__(self, parent=None):
        Tk.Frame.__init__(self, parent, bd=2)

        # Configure the root window.
        root = self.master
        mb = Tk.Menu(root)
        root.configure(menu=mb)
        root.resizable(False, False)
        root.title(info.__title__)

        # Add menus.
        m = Tk.Menu(mb, tearoff=False)
        mb.add_cascade(label="Game", menu=m, underline=0)

        m.add_command(label="New", underline=0,
                      command=lambda: self.newgame((6, 7)))

        m.add_command(label="New (6 letters only)", underline=5,
                      command=lambda: self.newgame([6]))

        m.add_command(label="New (7 letters only)", underline=5,
                      command=lambda: self.newgame([7]))

        m.add_separator()
        m.add_command(label="Quit", underline=0, command=root.quit)

        m = Tk.Menu(mb, tearoff=False, name="help")
        mb.add_cascade(label="Help", menu=m, underline=0)
        m.add_command(label="About", underline=0, command=self.about)
        m.add_command(label="Web Site", underline=0, command=self.website)

        # Add board frame.
        self.boards = []
        self.boardframe = frame = Tk.Frame(self)
        frame.grid(row=0, column=0)

        # Add text entry.
        entry = self.entry = Tk.Entry(self, width=12, font=("Courier", 10))
        entry.bind("<Return>", self.tryword)
        entry.focus_set()
        entry.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Add status label.
        status = self.statusbar = Tk.Label(self, relief=Tk.SUNKEN,
                                           anchor=Tk.W)
        status.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Start a new game.
        self.newgame()

        # Start things up.
        self.pack()

    def newgame(self, boards=(6, 7)):
        "Start a new game."

        self.score = 0
        self.boardidx = 0

        for board in self.boards:
            board.destroy()

        self.boards = []
        for col, count in enumerate(boards):
            board = BoardFrame(self.boardframe, count)
            board.grid(row=0, column=col, padx=3, pady=5)
            self.boards.append(board)

        self.nextword()

    def tryword(self, event):
        "Try a word entered in the entry box."

        # If the game's over, do nothing.
        if self.current.board.complete:
            return

        try:
            # Try the word.
            word = self.entry.get()
            score = self.current.board.guess(word)
        except ValueError, msg:
            # Invalid word.
            self.status(str(msg).capitalize())
        else:
            # Valid word.

            # Remove text from the entry.
            self.entry.delete(0, len(word))

            # Add word to the board display.
            row = len(self.current.board.guesses) - 1
            word = self.current.board.guesses[row]
            self.current.addword(row, word, score)

            if self.current.board.complete:
                # Board is complete -- add the actual word and total score.
                self.current.addword(row + 1, self.current.board.word,
                                     self.current.board.totalscore)

                # Update the final total.
                self.score += self.current.board.totalscore

                # Move to the next board, or report final score.
                if self.boardidx < len(self.boards) - 1:
                    self.boardidx += 1
                    self.nextword()
                else:
                    self.status("Your total score is %d" % self.score)
            else:
                # Board not finished; prompt for next word.
                self.nextword()

    def about(self):
        import tkMessageBox as box

        lines = ["%s version %s" % (info.__title__, info.__version__),
                 info.__desc__,
                 "Written by %s <%s>" % (info.__author__, info.__email__),
                 "License: %s" % info.__license__]

        box.showinfo("About", "\n\n".join(lines))

    def website(self):
        import webbrowser
        webbrowser.open_new_tab(info.__url__)

    @property
    def current(self):
        "Current board frame."
        return self.boards[self.boardidx]

    def nextword(self):
        self.status("Enter a %d-letter word" %
                    self.current.board.nextwordsize())

    def status(self, msg):
        self.statusbar.configure(text=msg)
        self.update_idletasks()


class BoardFrame(Tk.Frame):
    "A frame containing a single board."

    def __init__(self, master, letters):
        Tk.Frame.__init__(self, master)

        # Create representation of the board.
        self.board = Board(letters)

        # Add frame with labels for guesses and result.
        frame = Tk.Frame(self, bd=2, relief=Tk.GROOVE)
        frame.pack()

        nrows = len(self.board.wordlen)
        ncols = len(self.board.word)

        self.letters = {}
        self.scores = []

        for row in xrange(nrows + 1):
            if row < nrows:
                foreground = "black"
                background = "lightblue"
                relief = Tk.GROOVE
            else:
                foreground = "red"
                background = "grey"
                relief = Tk.FLAT

            for col in xrange(ncols):
                label = Tk.Label(frame, width=2, font=("Courier", 24, "bold"),
                                 fg=foreground, bg=background, relief=relief)
                self.letters[row, col] = label
                label.grid(row=row, column=col)

            label = Tk.Label(frame, width=5, height=1, font=("Courier", 24),
                             bg="pink", relief=Tk.FLAT)
            self.scores.append(label)
            label.grid(row=row, column=ncols)

        # Paint the letter labels white.
        for row in xrange(nrows):
            offset = self.board.offsets[row]
            wordlen = self.board.wordlen[row]
            for col in xrange(offset, offset + wordlen):
                label = self.letters[row, col]
                label.configure(bg="white", relief=Tk.SUNKEN)

        # Add checkbuttons for each letter.
        frame = Tk.Frame(self, bd=2, relief=Tk.GROOVE)
        frame.pack(pady=5)

        for num, letter in enumerate(string.uppercase):
            row = 0 if num < 13 else 1
            col = num % 13
            button = Tk.Checkbutton(frame, width=1, height=1, indicatoron=0,
                                    font=("Courier", 12), text=letter,
                                    selectcolor="red")
            button.grid(row=row, column=col)

    def addword(self, row, word, score):
        "Add a word and score to the grid."

        for col, letter in enumerate(word):
            if letter in string.letters:
                label = self.letters[row, col]
                label.configure(text=letter)

        label = self.scores[row]
        label.configure(text=str(score).rjust(5))


class Board(object):
    "A game board."

    def __init__(self, word_or_size, dictionary=None):
        self.dict = dictionary if dictionary else Dictionary()

        if isinstance(word_or_size, str):
            self.word = word_or_size.upper()
            wordsize = len(self.word)
            if self.word not in self.dict:
                raise ValueError("'%s' is not a word" % self.word)
        elif isinstance(word_or_size, int):
            wordsize = word_or_size
            self.word = self.dict.random(wordsize)
        else:
            raise RuntimeError("invalid argument: %s" % word_or_size)

        if wordsize not in (6, 7):
            raise RuntimeError("hidden word size must be 6 or 7")

        wordlen = [2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6]
        offsets = [0, 0, 1, 2, 3, 2, 1, 0, 0, 1, 0]

        self.wordlen = [n + wordsize - 6 for n in wordlen]
        self.offsets = offsets

        self.guesses = []
        self.scores = []
        self.totalscore = 0
        self.complete = False

    def guess(self, word):
        "Guess a word and return its score."

        # Check word is the right length.
        wordsize = self.nextwordsize()
        if len(word) != wordsize:
            raise ValueError("word must have %d letters" % wordsize)

        # Check it's a valid word.
        word = word.upper()
        if word not in self.dict:
            raise ValueError("that is not a word")

        word = self.normalize(word)
        self.guesses.append(word)

        # Calculate score.
        score = 0
        guess = list(word)
        actual = list(self.word)

        for i in xrange(len(guess)):
            if guess[i] == actual[i]:
                guess[i] = actual[i] = " "
                score += 1000

        for letter in actual:
            if letter != " " and letter in guess:
                guess.remove(letter)
                score += 250

        # Update score.
        self.scores.append(score)
        self.totalscore += score

        # Add guessed-the-word bonus.
        if word == self.word:
            self.totalscore += 3000

        # Flag completed.
        if len(self.guesses) == len(self.wordlen):
            self.complete = True

        return score

    def nextwordsize(self):
        "Return required word size of the next guess."
        num = len(self.guesses)
        return self.wordlen[num]

    def normalize(self, string=None, sep="."):
        "Normalize a string according to the next guess."

        # Get length and offset.
        num = len(self.guesses)
        wordlen = self.wordlen[num]
        offset = self.offsets[num]

        if string is None:
            string = "_" * wordlen

        # Pad out to right length with blanks.
        rblank = len(self.word) - wordlen - offset
        return sep * offset + string + sep * rblank

    def display(self):
        "Return string representation of the round."

        def expand(string):
            return "".join([c + " " for c in string])

        s = ""
        for guess, score in zip(self.guesses, self.scores):
            s += expand(guess) + "  %d\n" % score

        if self.complete:
            s += "\nTotal score: %d\n" % self.totalscore
        else:
            s += expand(self.normalize()) + "\n"

        return s

    def __str__(self):
        return self.display()


class Dictionary(set):
    "Dictionary of valid words."

    def __init__(self, wordlist=None):
        if not wordlist:
            path = resource_filename(__name__, "words.dat")
            wordlist = []
            with open(path) as fp:
                for line in fp:
                    if not line.startswith('#'):
                        words = line.split()
                        wordlist.extend(words)

        for word in wordlist:
            self.add(word.upper())

    def random(self, size):
        "Return a random word of given size."
        words = [word for word in self if len(word) == size]
        return random.choice(words)


def play():
    Game().mainloop()


if __name__ == "__main__":
    play()
