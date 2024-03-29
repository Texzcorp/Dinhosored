import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import keyboard
import mouse
from mouse import ButtonEvent, hook
from pynput import mouse as pymouse
import threading
import time
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QApplication
import os
import sys
import winreg
import tkinter.font as tkFont
from pathlib import Path

class DishonoredSpeedrunBhopMacro:
    def __init__(self):
        super().__init__()
        # Chemin vers le dossier de données
        self.script_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.script_dir, "data")
        self.s_data_dir = self.get_user_data_dir("Dinhosored")
        # Initialize variables
        self.g_pressed_up = False
        self.g_pressed_down = False
        self.scroll_up_thread = None
        self.scroll_down_thread = None 
        self.interval = 5  # Default interval in milliseconds
        self.interval_up = 1200
        self.interval_down = 400
        self.isModifierUp = False  # Variable to store if the trigger key is a modifier key
        self.isModifierDown = False # Variable to store if the trigger key is a modifier key
        self.is_modifier = False
        self.key_hook_callback = None
        self.logo_size = (3, 3)
        self.is_keyboard_up = None
        self.is_keyboard_down = None
        self.trigger_key_down = None
        self.trigger_key_up = None
        self.any_scroll_thread = None
        self.kill_any_scroll_thread = False

        self.start_any_scroll()

        self.direction = 0

        # Create a Qt application
        self.app = QtWidgets.QApplication(sys.argv)

        # Load fonts from the specified directory
        font_path = os.path.join(self.data_dir, "fonts")
        # font_dir = DIR_APPLICATION / "fonts"
        families = self.load_fonts_from_dir(font_path)

        # Load assigned keys and interval
        self.load_data()

        # Setup listener for key events
        keyboard.hook(self.on_action)
        mouse.hook(self.on_action)

        # Create a Tkinter window
        self.root = tk.Tk()
        self.root.title("Dinhosored")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Chemin vers le fichier ICO relatif au répertoire du script
        icon_path = os.path.join(self.data_dir, "Dinhosored.ico")

        # Change window icon
        self.root.iconbitmap(icon_path)

        # Set window transparency
        self.root.attributes('-alpha', 0.93)

        # Couleur principale
        main_color = '#060c14'

        # Couleur pour les boutons
        button_color = '#060c14'  

        # Couleur de survol pour les boutons
        hover_color = '#000000'  

        # Couleur de la police pour les boutons
        text_color = '#e0d346' 

        # Create and place a frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.frame.configure(bg=main_color, bd=2, relief=tk.RAISED)  # Adjust background color and border

        # Alternative way to set the font family for tkinter
        if families:
            font_family = families[0]  # Assuming you want to use the first font family found
            self.custom_font = tkFont.Font(family=font_family, size=14)

        title_font_path = os.path.join(self.data_dir, "fonts", "OptimusPrinceps.ttf")

        # Create a Font object
        # if os.path.isfile(font_path):
        #     self.custom_font = tkFont.Font(family="Dream Orphans", size=14)
        if os.path.isfile(title_font_path):
            self.title_font = tkFont.Font(family="OptimusPrinceps", size=84)  # Assign to self.title_font here
        # else:
        #     self.custom_font = tkFont.Font(family="Arial", size=12)  # Use a default font if the custom font file is not found
        
        # Load the logo image
        logo_path = os.path.join(self.data_dir, "logo.png")
        if os.path.isfile(logo_path):
            self.logo_img = tk.PhotoImage(file=logo_path)
        else:
            self.logo_img = None

        self.isPro = False

        # Create a custom style and configure it with the custom font
        self.custom_style = ttk.Style()
        self.custom_style.theme_use('alt')
        self.custom_style.configure("Custom.TButton", font=self.custom_font, relief=tk.RAISED, foreground=text_color, background=button_color)   # Adjust button relief
        self.custom_style.map("Custom.TButton", background=[('active', hover_color)])  # Adjust button hover color

        self.pro_style = ttk.Style()
        self.pro_style.configure("Pro.TButton", font = (self.custom_font, 10), relief=tk.RAISED, foreground="#6376a8", background=button_color)   # Adjust button relief
        self.pro_style.map("Pro.TButton", background=[('active', hover_color)])  # Adjust button hover color

        # Create a custom style for the labels with transparent background
        self.custom_style_label = ttk.Style()
        self.custom_style_label.configure("Transparent.TLabel", font=self.custom_font, background=self.frame.cget("background"), foreground=text_color)  # Set background to frame's background color

        # Create a custom style for the labels with transparent background
        self.estyle = ttk.Style()
        self.estyle.element_create("plain.field", "from", "default")
        self.estyle.layout("EntryStyle.TEntry",
                           [('Entry.plain.field', {'children': [(
                               'Entry.background', {'children': [(
                                   'Entry.padding', {'children': [(
                                       'Entry.textarea', {'sticky': 'nswe'})],
                                      'sticky': 'nswe'})], 'sticky': 'nswe'})],
                              'border':'2', 'sticky': 'nswe'})])
        self.estyle.configure("EntryStyle.TEntry",
                              background="#263145",
                              foreground=text_color,
                              fieldbackground="#263145")

        # Create a custom style for the title label
        self.title_style = ttk.Style()
        self.title_style.configure("Title.TLabel", font=(self.title_font), foreground=text_color, background=main_color)

        # Create and place the logo
        if self.logo_img:
            self.logo_img = self.logo_img.subsample(*self.logo_size)  # Resize the logo image
            self.logo_label = ttk.Label(self.frame, image=self.logo_img, style="Transparent.TLabel")
            self.logo_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Create and place the title label
        self.title_label = ttk.Label(self.frame, text="Dinhosored", style="Title.TLabel")
        self.title_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Create and place a label for interval selection
        self.interval_label_down = ttk.Label(self.frame, text="Interval down (ms):", style="Transparent.TLabel")
        self.interval_label_down.grid(row=7, column=0, padx=5, pady=5, sticky="w")

        # Create and place an entry for interval input
        self.interval_entry_down = ttk.Entry(self.frame, font=self.custom_font, style="EntryStyle.TEntry")
        self.interval_entry_down.insert(0, str(self.interval_down))
        self.interval_entry_down.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        # Create and place a button to set the interval
        self.set_interval_button_down = ttk.Button(self.frame, text="Set Interval", command=self.set_interval_down, style="Custom.TButton")
        self.set_interval_button_down.grid(row=7, column=2, padx=5, pady=5, sticky="w")

        # Create and place a label for interval selection
        self.interval_label_up = ttk.Label(self.frame, text="Interval up (ms):", style="Transparent.TLabel")
        self.interval_label_up.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Create and place an entry for interval input
        self.interval_entry_up = ttk.Entry(self.frame, font=self.custom_font, style="EntryStyle.TEntry")
        self.interval_entry_up.insert(0, str(self.interval_up))
        self.interval_entry_up.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Create and place a button to set the interval
        self.set_interval_button_up = ttk.Button(self.frame, text="Set Interval", command=self.set_interval_up, style="Custom.TButton")
        self.set_interval_button_up.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Create and place a label to display the current trigger key for scrolling down
        self.trigger_key_label_down = ttk.Label(self.frame, text=f"Current Scroll Down Key: {self.trigger_key_down}", style="Transparent.TLabel")
        self.trigger_key_label_down.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # Create and place a button to assign another key for scrolling down
        self.assign_key_button_down = ttk.Button(self.frame, text="Assign Scroll Down Key", command=lambda: self.update_trigger_keys("down"), style="Custom.TButton")
        self.assign_key_button_down.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Create and place a label to display the current trigger key for scrolling down
        self.trigger_key_label_empty = ttk.Label(self.frame, text=f" ", style="Transparent.TLabel")
        self.trigger_key_label_empty.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # Create and place a label to display the current trigger key for scrolling up
        self.trigger_key_label_up = ttk.Label(self.frame, text=f"Current Scroll Up Key: {self.trigger_key_up}", style="Transparent.TLabel")
        self.trigger_key_label_up.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # Create and place a button to assign another key for scrolling up
        self.assign_key_button_up = ttk.Button(self.frame, text="Assign Scroll Up Key", command=lambda: self.update_trigger_keys("up"), style="Custom.TButton")
        self.assign_key_button_up.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Create and place a button to assign another key for scrolling up
        self.pro_button = ttk.Button(self.frame, text="100% pro Mode", command=self.promode, style="Pro.TButton")
        self.pro_button.grid(row=8, column=2, padx=5, pady=5, sticky="es")

        # Configure grid columns and rows to expand uniformly
        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=1)
        self.frame.grid_rowconfigure(5, weight=1)

        # Keep the Tkinter window running
        self.root.mainloop()

    def on_close(self):
        print("Fenêtre fermée")
        self.kill_any_scroll_thread = True
        self.any_scroll_thread.join()
        self.root.destroy()

    # # Function to continuously spam the scroll wheel event
    # def spam_scroll_up(self, direction):
    #     self.direction = direction
    #     current_counter = 0
    #     while True:
    #         previous_counter = current_counter
    #         current_counter = time.perf_counter_ns()
    #         if previous_counter != 0:
    #             print(current_counter - previous_counter)
    #         if not self.g_pressed_up:
    #             break
    #         pymouse.Controller().scroll(0, direction)
    #         time.sleep(self.interval / 1000)  # Sleep for the specified interval in milliseconds


    #     # Function to continuously spam the scroll wheel event
    # def spam_scroll_down(self, direction):
    #     self.direction = direction
    #     current_counter = 0
    #     while True:
    #         previous_counter = current_counter
    #         current_counter = time.perf_counter_ns()
    #         if previous_counter != 0:
    #             print(current_counter - previous_counter)
    #         if not self.g_pressed_down:
    #             break
    #         pymouse.Controller().scroll(0, direction)
    #         time.sleep(self.interval / 1000)  # Sleep for the specified interval in milliseconds

    def gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def spam_any_scroll(self):
        gcd_interval = self.gcd(self.interval_down, self.interval_up)
        down_factor = self.interval_down // gcd_interval
        up_factor = self.interval_up // gcd_interval
        cpt = 0


        while not self.kill_any_scroll_thread:
            if self.g_pressed_down ^ self.g_pressed_up:
                cpt += 1

                if cpt % self.interval_down == 0 and self.g_pressed_down:
                    pymouse.Controller().scroll(0, -1)
                    time.sleep(self.interval_down / 1000 / 1)
                    print(str(self.interval_down / 1000 / 1))

                if cpt % self.interval_up == 0 and self.g_pressed_up:
                    pymouse.Controller().scroll(0, 1)
                    time.sleep(self.interval_up / 1000 / 1)
                    print(str(self.interval_up / 1000 / 1))

            elif self.g_pressed_down and self.g_pressed_up:
                cpt += 1

                if cpt % self.interval_down == 0 and self.g_pressed_down:
                    pymouse.Controller().scroll(0, -1)
                    time.sleep(self.interval_down / 1000 / down_factor)
                    print("down" + str(self.interval_down / 1000 / down_factor))

                if cpt % self.interval_up == 0 and self.g_pressed_up:
                    pymouse.Controller().scroll(0, 1)
                    time.sleep(self.interval_up / 1000 / up_factor)
                    print("up" + str(self.interval_up / 1000 / up_factor))
                
            else:
                time.sleep(0.001)

    # Function to handle key events
    def on_action(self, event):
        if type(event) == keyboard.KeyboardEvent:
            key_name = event.name.lower()  # Convert key name to lowercase
            if not self.is_modifier:
                for modifier in ['alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows', 'shift', 'windows']:
                    if modifier in key_name:
                        key_name = key_name.replace(modifier, '')
            if event.event_type == keyboard.KEY_DOWN:
                if key_name == self.trigger_key_down:
                    # self.start_scroll_down()
                    self.g_pressed_down = True
                elif key_name == self.trigger_key_up:
                    # self.start_scroll_up()
                    self.g_pressed_up = True
            elif event.event_type == keyboard.KEY_UP:
                if key_name == self.trigger_key_down:
                    self.g_pressed_down = False
                elif key_name == self.trigger_key_up:
                    self.g_pressed_up = False
        elif type(event) == mouse.ButtonEvent:
            key_name = ("mouse_" + event.button)
            if event.event_type == mouse.DOWN:
                if  key_name == self.trigger_key_down:
                    # self.start_scroll_down()
                    self.g_pressed_down = True
                elif key_name == self.trigger_key_up:
                    # self.start_scroll_up()
                    self.g_pressed_up = True
            elif event.event_type == mouse.UP:
                if key_name == self.trigger_key_down:
                    self.g_pressed_down = False
                elif key_name == self.trigger_key_up:
                    self.g_pressed_up = False

    # def start_scroll_down(self):
    #     if not self.scroll_down_thread or not self.scroll_down_thread.is_alive():
    #         self.g_pressed_down = True
    #         self.scroll_down_thread = threading.Thread(target=self.spam_scroll_down, args=(-1,))
    #         self.scroll_down_thread.start()
    #     # elif self.direction != -1:
    #     #     self.g_pressed = False
    #     #     while self.scroll_down_thread.is_alive():
    #     #         pass
    #     #     self.g_pressed = True
    #     #     self.scroll_down_thread = threading.Thread(target=self.spam_scroll_down, args=(-1,))
    #     #     self.scroll_down_thread.start()

    # def start_scroll_up(self):
    #     if not self.scroll_up_thread or not self.scroll_up_thread.is_alive():
    #         self.g_pressed_up = True
    #         self.scroll_up_thread = threading.Thread(target=self.spam_scroll_up, args=(1,))
    #         self.scroll_up_thread.start()
    #     # elif self.direction != 1:
    #     #     self.g_pressed = False
    #     #     while self.scroll_up_thread.is_alive():
    #     #         pass
    #     #     self.g_pressed = True
    #     #     self.scroll_up_thread = threading.Thread(target=self.spam_scroll_up, args=(1,))
        #     self.scroll_up_thread.start()
            
    def start_any_scroll(self):
        self.any_scroll_thread = threading.Thread(target=self.spam_any_scroll)
        self.any_scroll_thread.start()

    # Function to handle interval selection
    def set_interval_down(self):
        self.interval_down = float(self.interval_entry_down.get())
        print(self.interval)
        self.save_data() #Save interval
        
    def set_interval_up(self):
        self.interval_up = float(self.interval_entry_up.get())
        print(self.interval)
        self.save_data() #Save interval

    # Function to update the trigger keys
    def update_trigger_keys(self, scroll_direction):
        if scroll_direction == "down":
            self.assign_key_button_down.config(text="Press a Key")
            self.assign_key_button_down.config(state=tk.DISABLED)
        elif scroll_direction == "up":
            self.assign_key_button_up.config(text="Press a Key")
            self.assign_key_button_up.config(state=tk.DISABLED)

        # Register hook
        self.key_hook_callback = lambda event: self.assign_key(event, scroll_direction)
        keyboard.hook(self.key_hook_callback)
        mouse.hook(self.key_hook_callback)

    def unregister_key_hook(self):
        if self.key_hook_callback:
            keyboard.unhook(self.key_hook_callback)
            mouse.unhook(self.key_hook_callback)
            self.key_hook_callback = None

    # Function to assign the pressed key as the new trigger key
    def assign_key(self, event, scroll_direction):
        
        if (type(event) == keyboard.KeyboardEvent):
            key_name = event.name.lower()
            self.is_modifier = any(modifier in key_name for modifier in ['alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows', 'shift', 'windows'])
            
            if scroll_direction == "down":
                self.trigger_keyboard_down = True
                self.trigger_key_down = key_name
                self.isModifierDown = any(modifier in key_name for modifier in ['alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows', 'shift', 'windows'])
            elif scroll_direction == "up":
                self.trigger_keyboard_up = True
                self.trigger_key_up = key_name
                self.isModifierUp = any(modifier in key_name for modifier in ['alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows', 'shift', 'windows'])
            
            # Save the assigned keys
        elif (type(event) == mouse.ButtonEvent):
            if scroll_direction == "down":
                self.trigger_keyboard_down = False
                self.trigger_key_down = "mouse_" + event.button
            elif scroll_direction == "up":
                self.trigger_keyboard_up = False
                self.trigger_key_up = "mouse_" + event.button
        else:
            return
        self.update_trigger_keys_after_assign(scroll_direction)
        self.unregister_key_hook()
        self.save_data()


    def update_trigger_keys_after_assign(self, scroll_direction):
        if scroll_direction == "down":
            self.trigger_key_label_down.config(text=f"Current Scroll Down Key: {self.trigger_key_down}")
            self.assign_key_button_down.config(text="Assign Another Key")
            self.assign_key_button_down.config(state=tk.NORMAL)
        elif scroll_direction == "up":
            self.trigger_key_label_up.config(text=f"Current Scroll Up Key: {self.trigger_key_up}")
            self.assign_key_button_up.config(text="Assign Another Key")
            self.assign_key_button_up.config(state=tk.NORMAL)

    def get_user_data_dir(self, appname: str) -> Path:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        )
        dir_, _ = winreg.QueryValueEx(key, "Local AppData")
        ans = Path(dir_).resolve(strict=False)
        return ans.joinpath(appname)

    # Function to save the assigned keys to a file
    def save_data(self):
        data_dir = self.s_data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)  # Create the directory if it doesn't exist
        data_file_path = os.path.join(data_dir, "data.txt")
        with open(data_file_path, "w") as file:
            file.write(f"trigger_key_down={self.trigger_key_down}\n")
            file.write(f"trigger_key_up={self.trigger_key_up}\n")
            file.write(f"interval_down={str(self.interval_down)}\n")
            file.write(f"interval_up={str(self.interval_up)}\n")
            file.write(f"is_keyboard_up={str(self.is_keyboard_up)}\n")
            file.write(f"is_keyboard_down={str(self.is_keyboard_down)}")

    # Function to load the assigned keys from a file
    def load_data(self):
        data_file_path = os.path.join(self.s_data_dir, "data.txt")
        if os.path.isfile(data_file_path):
            with open(data_file_path, "r") as file:
                for line in file:
                    # Check if the line contains '=' to avoid ValueError
                    if '=' in line:
                        key, value = line.strip().split("=")
                        if key == "trigger_key_down":
                            self.trigger_key_down = value
                        elif key == "trigger_key_up":
                            self.trigger_key_up = value
                        elif key == "interval_down":
                            self.interval_down = float(value)
                        elif key == "interval_up":
                            self.interval_up = float(value)
                        elif key == "is_keyboard_up":
                            self.is_keyboard_up = (value == "True")
                        elif key == "is_keyboard_down":
                            self.is_keyboard_down = (value == "True")

    # Function to load fonts from a directory
    def load_fonts_from_dir(self, directory):
        families = set()
        for fi in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
            _id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
            families |= set(QFontDatabase.applicationFontFamilies(_id))
        return list(families)

    # Function for the pro mode
    def promode(self):
        if self.isPro:
            font_path = os.path.join(self.data_dir, "fonts", "Dream Orphans Bd.otf")
            if os.path.isfile(font_path):
                # self.custom_font = tkFont.Font(family="Dream Orphans", size=14)
                self.custom_style.configure("Custom.TButton", font=self.custom_font)
                self.custom_style_label.configure("Transparent.TLabel", font=self.custom_font)
                self.pro_style.configure("Pro.TButton", font = (self.custom_font, 10))
                self.title_style.configure("Title.TLabel", font=(self.title_font))
            self.isPro = False
        else:
            font_path = os.path.join(self.data_dir, "fonts", "Dh_script-Regular.otf")
            if os.path.isfile(font_path):
                self.pcustom_font = tkFont.Font(family="Dh_script", size=17)
                self.custom_style.configure("Custom.TButton", font=self.pcustom_font)
                self.custom_style_label.configure("Transparent.TLabel", font=self.pcustom_font)
                self.pro_style.configure("Pro.TButton", font = (self.pcustom_font))
                self.tcustom_font = tkFont.Font(family="Dh_script", size=79)
                self.title_style.configure("Title.TLabel", font=(self.tcustom_font))
            self.isPro = True

# Create an instance of the class
DishonoredSpeedrunBhopMacro()