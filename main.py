import sys

import spotify_utils as spot
from tkinter import Tk, StringVar, ttk, font, W, Label, Entry, Button, CENTER, Frame
from lyrics import Lyrics

# Configuration
SESSION_FILE = 'session.cfg'
client_id = '42b30bf40e884b378c2d4f6989585147'
client_secret = 'a057c8a973574c13857e6dd136a8fa1b'
redirect_uri = 'http://localhost:4304/auth/spotify/callback'

# View
WIDTH, HEIGHT = 500, 280  # Defines aspect ratio of window.
COLOR_PLATINUM = "#E0E0DE"
COLOR_EERIE_BLACK = "#242423"

root = None
current_msg = None
current_lyric = None
msg_label = None
current_scale_msg = None
lyric_label = None
id_field = None
id_label = None
secret_field = None
secret_label = None
callback_field = None
callback_label = None
error_label = None
submit_button = None
user_spotify = None
scale = None


def start_window():
    global root, current_msg, current_lyric, user_spotify
    root = Tk()
    root.withdraw()
    root.title("LyricSpot")
    root.iconbitmap("icon.ico")
    current_msg = StringVar()
    current_lyric = StringVar()

    # Calculate geometry
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (WIDTH / 2))
    y_coordinate = int((screen_height / 2) - (HEIGHT / 2))
    root.geometry(
        "{}x{}+{}+{}".format(WIDTH, HEIGHT, x_coordinate, y_coordinate))

    # Set styles
    label_style = ttk.Style()
    label_style.configure("BW.Label", background=COLOR_EERIE_BLACK, foreground=COLOR_PLATINUM)

    root.resizable(False, False)
    root.configure(bg=COLOR_EERIE_BLACK)

    spotify, user_spotify = spot.try_get_spotify_session_from_file(SESSION_FILE)

    if not user_spotify:
        set_start_screen()
    else:
        set_lyric_screen()

    # Show
    root.deiconify()
    root.mainloop()


# Create a custom button class
class CustomButton(Label):
    def __init__(self, *args, **kwargs):
        on_click_func = kwargs.pop("on_click_func", None)

        def on_enter(event):
            event.widget.configure(cursor="hand2")
            self.configure(bg=self.hover_bg)

        def on_leave(event):
            event.widget.configure(cursor="")
            self.configure(bg=self.default_bg)

        def on_click(func):
            self.configure(bg=self.active_bg)
            if func and callable(func):
                func()

        def on_release(event):
            self.configure(bg=self.hover_bg)

        kwargs["bg"] = COLOR_PLATINUM
        kwargs["fg"] = COLOR_EERIE_BLACK
        kwargs["font"] = ("Calibri", 14)
        kwargs["relief"] = "flat"
        self.default_bg = COLOR_PLATINUM
        self.hover_bg = "white"
        self.active_bg = "lightgray"
        super().__init__(*args, **kwargs)
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.bind("<Button-1>", lambda event: on_click(on_click_func))
        self.bind("<ButtonRelease-1>", on_release)


# Define a custom entry class with desired styling
class CustomEntry(Entry):
    def __init__(self, *args, **kwargs):
        kwargs["bg"] = COLOR_EERIE_BLACK
        kwargs["fg"] = COLOR_PLATINUM
        kwargs["width"] = 35
        kwargs["insertbackground"] = COLOR_EERIE_BLACK
        kwargs["highlightcolor"] = COLOR_PLATINUM
        kwargs["highlightthickness"] = 1
        kwargs["font"] = ("Calibri", 14)
        kwargs["relief"] = "flat"
        kwargs["selectbackground"] = COLOR_PLATINUM
        kwargs["selectforeground"] = COLOR_EERIE_BLACK
        super().__init__(*args, **kwargs)

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        self.update_style(False)

    def on_focus_in(self, event):
        self.update_style(True)

    def on_focus_out(self, event):
        self.update_style(False)

    def update_style(self, in_focus):
        if in_focus:
            self.configure(bg=COLOR_PLATINUM, fg=COLOR_EERIE_BLACK, selectbackground=COLOR_EERIE_BLACK,
                           selectforeground=COLOR_PLATINUM)
        else:
            self.configure(bg=COLOR_EERIE_BLACK, fg=COLOR_PLATINUM, selectbackground=COLOR_PLATINUM,
                           selectforeground=COLOR_EERIE_BLACK)


def try_submit_config():
    global user_spotify, error_label, submit_button
    conf = (id_field.get(), secret_field.get(), callback_field.get())

    id_label.pack_forget()
    secret_label.pack_forget()
    id_field.pack_forget()
    secret_field.pack_forget()
    submit_button.pack_forget()
    callback_field.delete(0, len(callback_field.get()))
    callback_label.configure(text="Redirect URL")

    def try_submit_callback():
        global user_spotify

        user_token = spot.get_token(callback_field.get())
        if user_token:
            spotify, user_spotify = spot.try_get_spotify_session(user_token, conf, SESSION_FILE)

        if user_token and user_spotify:
            error_label.pack_forget()
            submit_button.pack_forget()
            callback_field.pack_forget()
            callback_label.pack_forget()
            root.update()
            set_lyric_screen()
        else:
            error_label.configure(text="Invalid Token, try again")

    submit_button = CustomButton(root, text="LOGIN", on_click_func=try_submit_callback)

    error_label = ttk.Label(root, text="Authorize and paste redirect URL", style="BW.Label", font=("Calibri", 16))
    submit_button.pack(pady=(15, 0))
    error_label.pack(pady=(100, 0))

    root.update()

    spot.open_browser_login(conf)






def set_start_screen():
    global id_field, secret_field, callback_field, submit_button, id_label, secret_label, callback_label

    # Define the labels
    id_label = ttk.Label(root, text="Client ID",  style="BW.Label", font=("Calibri", 14))
    secret_label = ttk.Label(root, text="Client Secret",  style="BW.Label", font=("Calibri", 14))
    callback_label = ttk.Label(root, text="Callback URL",  style="BW.Label", font=("Calibri", 14))

    # Create the entry fields
    id_field = CustomEntry(root)
    secret_field = CustomEntry(root)
    callback_field = CustomEntry(root)

    id_field.insert(0, client_id)
    secret_field.insert(0, client_secret)
    callback_field.insert(0, redirect_uri)

    # Function to unfocus the entry fields
    def unfocus_entry_fields(event):
        if event.widget not in (id_field, secret_field, callback_field):
            root.focus_set()  # Set focus on the root window

    # Bind the <Button-1> event on the root window to unfocus the entry fields
    root.bind("<Button-1>", unfocus_entry_fields)

    # Create the submit button
    submit_button = CustomButton(root, text="SUBMIT", on_click_func=try_submit_config)

    # Arrange the labels and entry fields in a column
    id_label.pack(pady=(10, 0))
    id_field.pack()

    secret_label.pack(pady=(10, 0))
    secret_field.pack()

    callback_label.pack(pady=(10, 0))
    callback_field.pack()

    submit_button.pack(pady=(15, 0))


def set_lyric_screen():
    global lyric_label, msg_label, scale, current_scale_msg

    fontLyric = font.Font(family="Calibri", size=20, weight="bold")
    lyric_label = ttk.Label(root, textvariable=current_lyric,
                                          style="BW.Label", font=fontLyric, wraplength=450,
                                          justify="center")
    msg_label = ttk.Label(root, textvariable=current_msg,
                                        style="BW.Label", font=("Calibri", 12), wraplength=400)
    msg_label.pack(padx=25, pady=15, anchor=W)
    lyric_label.pack(pady=50)
    current_lyric.set("Play a song :)")
    current_scale_msg = StringVar()
    current_scale_msg.set("Anticipation: 200 ms")

    def handle_scale_change(value):
        new_value = int(scale.get() / 50) * 50
        if new_value != scale.get():
            scale.set(new_value)
            if new_value == 0:
                current_scale_msg.set("0 ms")
            elif new_value < 0:
                current_scale_msg.set("Delay: " + str(new_value*-1) + " ms")
            else:
                current_scale_msg.set("Anticipation: " + str(new_value) + " ms")

    def on_enter_scale_frame(event):
        scale_label.pack(pady=(0, 5))
        scale.pack()

    def on_leave_scale_frame(event):
        scale_label.pack_forget()
        scale.pack_forget()

    scale_frame = ttk.Frame(root, style="BW.Label")
    scale_frame.place(relx=0.5, rely=0.85, anchor=CENTER)

    scale_style = ttk.Style()
    scale_style.configure("Custom.Horizontal.TScale", background=COLOR_EERIE_BLACK, troughcolor="blue")
    scale_label = ttk.Label(scale_frame, textvariable=current_scale_msg,
                                        style="BW.Label", font=("Calibri", 12), wraplength=400)
    scale = ttk.Scale(scale_frame, from_=-510, to=510, length=200, orient="horizontal", command=handle_scale_change, style="Custom.Horizontal.TScale")

    scale.set(200)  # Set the initial value

    scale_frame.bind("<Enter>", on_enter_scale_frame)
    scale_frame.bind("<Leave>", on_leave_scale_frame)

    scale_label.pack(pady=(0, 5))
    scale.pack()

    root.update()
    on_leave_scale_frame(None)

    Lyrics.start_lyrics_thread(user_spotify, current_msg, current_lyric, scale)



start_window()
#spotify, user_spotify = spot.get_spotify_session(conf, SESSION_FILE)

























