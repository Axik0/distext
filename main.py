from tkinter import *
from PIL import Image, ImageTk
import string
import time
import threading

# prepare character lists for future key bindings
LETTERS_L = set(string.ascii_lowercase)
LETTERS_U = set(string.ascii_uppercase)
DIGITS = set(string.digits)
# wow, this list automation takes even care of the problematic cases (includes both "'" and '"')
MARKS = set(string.punctuation)-{"#"}
EXTRAS = ['<space>']

charset = set.union(LETTERS_L, LETTERS_U, EXTRAS, MARKS-{"<"})
markset = set.union(MARKS-{"<"}, {" "})


# image import&resize (non-crappy now thanks to this pillow fork)
icon = Image.open("images/clock.png")
icon = icon.resize((20, 20), Image.Resampling.LANCZOS)
rfr = Image.open("images/refresh.png")
rfr = rfr.resize((35, 35), Image.Resampling.LANCZOS)
cp = Image.open("images/files.png")
cp = cp.resize((35, 35), Image.Resampling.LANCZOS)

# Global color palette
main_color = '#f0f3f5'
focus_color = '#fff0fb'
text_color_a = '#262626'
text_color_ina = '#848484'

# Global font
main_font = ("Helvetica", 16)

# GUI preliminaries
window = Tk()
window.configure(background=main_color)
window.geometry("520x370")
window.minsize(520, 370)
window.maxsize(520, 370)
window.title("Disappearing text")
icon_tk = ImageTk.PhotoImage(icon)
window.iconphoto(False, icon_tk)


def save_text():
    """ copy all text_field contents to clipboard"""
    inp = text_field.get("1.0", 'end-1c')
    # if this button was pressed, stop the loop
    global stop
    stop = True
    window.clipboard_clear()
    window.clipboard_append(inp)


tic = DoubleVar(value=0)
chars = IntVar(value=0)

def check(key_pressed):
    """compares an event (some symbol has just been typed) with a next symbol (on the right) of the text line"""
    tic.set(time.perf_counter())
    chars.set(chars.get() + 1)


def binder(command, lst=charset, mode=True):
    """takes key names from the list and binds/unbinds to/from a single callback"""
    for key in lst:
        text_field.bind(key, command) if mode else text_field.unbind(key)


stop = False


def disappear_init():
    global stop
    text_field.configure(state=NORMAL)
    text_field.delete("1.0", "end")
    save_butt.configure(state=DISABLED)
    # get delay value from the slider
    delay = window.dset.get()
    # retrieve the rules label and update its text
    info_label.grid(row=1, column=0, columnspan=2, pady=5)
    info_label.configure(text=f"Start typing and don't stop for more than {delay} s")
    # bind keys and callback of the proper charset to catch inputs from keyboard
    binder(check, charset)
    # get text_field dimensions to measure text length limit
    length_limit = text_field.cget('height') * text_field.cget('width')
    window.wait_variable(tic)
    # remove the label from our layout completely, if you just delete its text it is still a bit visible
    info_label.grid_forget()
    while not stop:
        toc = time.perf_counter()
        # measure the time since the last keypress event (if it ever happened)
        # wait variable has made this condition useless, but let it be, just in case
        delta = toc-tic.get() if tic.get() else 0
        print(delta)
        if delta >= delay:
            print('end')
            text_field.delete("1.0", "end")
            break
        # or just wait until we fill a whole text_field
        elif chars.get() == length_limit:
            # stop here and allow to save input
            save_butt.configure(state=NORMAL)
            break
        # allow to save progress but don't stop now (will be stopped later by the stop flag in keypress event)
        elif chars.get() >= length_limit/2:
            save_butt.configure(state=NORMAL)
        # blinking states, one makes all the text gray before it's gone, the second case reverts it
        # those values are experimental, larger intervals tend to distort the frequency of theblinking cursor
        elif delay*0.7 <= delta <= delay*0.72:
            text_field.configure(fg=text_color_ina)
        elif 0 <= delta <= delay*0.02:
            text_field.configure(fg=text_color_a)
    # revert all variables, disable text_field and unbind keys
    text_field.configure(state=DISABLED)
    binder(check, charset, False)
    tic.set(0)
    chars.set(0)


def runner():
    global stop
    stop = True
    if thr1.is_alive():
        print("something's wrong, thread still active, try again")
        stop = True
    else:
        print('thread stopped')
    stop = False
    thr = threading.Thread(target=disappear_init)
    thr.start()


head_label = Label(window, text="Disappearing text", font=main_font, bg=main_color)
head_label.grid(row=0, column=0, columnspan=2, pady=5)

text_field = Text(window, bg=focus_color, fg=text_color_a, height=10, width=40, font=main_font, relief=SUNKEN)
text_field.focus_set()
text_field.grid(row=1, column=0, columnspan=2, padx=18)

window.dset = IntVar(value=2)
dl = Scale(window, from_=1, to=10, orient=HORIZONTAL, length=250, tickinterval=1, showvalue=False,
           font=main_font, label='DELAY', variable=window.dset, resolution=1,
           troughcolor=focus_color, highlightbackground=main_color, bg=main_color)
dl.grid(row=2, column=0, sticky=N+S+W+E, padx=30)

info_label = Label(window, text=f"Start typing and don't stop for more than {dl.get()} s", font=main_font, bg=focus_color)
info_label.grid(row=1, column=0, columnspan=2, pady=5)

rfr_tk = ImageTk.PhotoImage(rfr)
cp_tk = ImageTk.PhotoImage(cp)

setup_container = Frame(window)
setup_container.grid(row=2, column=1)

retry_butt = Button(setup_container, text='Retry', image=rfr_tk, command=runner, bg=main_color)
retry_butt.grid(row=0, column=0, ipady=5, ipadx=5, pady=20, sticky=N+S+W+E)
save_butt = Button(setup_container, text='Retry', image=cp_tk, command=save_text, bg=main_color, state=DISABLED)
save_butt.grid(row=0, column=1, ipady=5, ipadx=5, padx=15, pady=20, sticky=N+S+W+E)


if __name__ == "__main__":
    thr1 = threading.Thread(target=disappear_init)
    thr1.start()




window.mainloop()