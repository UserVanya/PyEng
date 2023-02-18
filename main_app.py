import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from pyeng_translator_win import TranslatorWindow
from pyeng_core import PyengCore
import keyboard
import pyperclip
import time
colors = {"darkgrey": "#393D47", "lightgrey": "#E5E5E5",
          "white": "#FFFFFF", "black": "#000000", "grey": "#C0C0C0"}
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.core = PyengCore()
        self.enter_cwd()
        self.tr_app = TranslatorWindow(self.core)
        self.bind_all("<Escape>", lambda event: self.tr_app.close_window())
        self.create_main_window()
    def translator_callback(self, event=None):
        if not self.tr_app.is_opened():
            self.tr_app.create_window(self)
        self.tr_app.set_focus()
        text = pyperclip.paste().replace("\n", " ").replace(chr(2), "")
        self.tr_app.add_text_to_translate(text)
        try:
            self.tr_app.do_translate()
        except:
            pass    
        #time.sleep(0.5)
    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
    def create_main_window(self):
        self.title("PyEng")
        width = 800
        height = 600
        center_x = int(self.winfo_screenwidth() / 2 - width//2)
        center_y = int(self.winfo_screenheight() / 2 - height//2)
        self.geometry(f"{width}x{height}+{center_x}+{center_y}")
        self.resizable(True, True)
        self.configure(bg=colors["darkgrey"])
        self.configure_grid()
        self.create_widgets()
    def create_translator_window(self):
        self.tr_app.create_window(self)
        #hide main window
        self.iconify()
    def enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def create_learn_window(self):
        pass
    def create_dictionary_window(self):
        pass    
    def create_translate_from_file_window(self):
        pass
    def handle_checkbutton_focus_article(self):
        if self.focus_article_enabled.get():
            self.hotkey_focus_article = keyboard.add_hotkey('ctrl+q', self.translator_callback)
            keyboard.add_hotkey('escape', self.tr_app.close_window, suppress=True)
        else:
            keyboard.remove_hotkey(self.hotkey_focus_article)
    def create_widgets(self):
        self.tranlator_button = tk.Button(self.master, text="Translator", command=self.create_translator_window, bg=colors["black"], fg=colors["white"])
        self.tranlator_button.grid(row=0, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        self.tranlator_button.configure(font=("Calibri", 20, "bold"))

        self.learn_button = tk.Button(self.master, text="Learn", command=self.create_learn_window, bg=colors["black"], fg=colors["white"])
        self.learn_button.grid(row=1, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        self.learn_button.configure(font=("Calibri", 20, "bold"))

        self.dictionary_button = tk.Button(self.master, text="Dictionary", command=self.create_dictionary_window, bg=colors["black"], fg=colors["white"])
        self.dictionary_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        self.dictionary_button.configure(font=("Calibri", 20, "bold"))

        self.translate_from_file_button = tk.Button(self.master, text="Translate from file", command=self.create_translate_from_file_window, bg=colors["black"], fg=colors["white"])
        self.translate_from_file_button.grid(row=3, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        self.translate_from_file_button.configure(font=("Calibri", 20, "bold"))

        self.focus_article_enabled = tk.BooleanVar()
        self.focus_article_checkbox = ttk.Checkbutton(
            self.master, text="Inline translations (press <Ctrl+C Ctrl-Q> to open translator window)", variable=self.focus_article_enabled, onvalue=True, offvalue=False)
        self.focus_article_checkbox.grid(row=4, column=1, sticky="e", padx=5, pady=5)
        self.focus_article_enabled.trace("w", lambda name, index, mode, sv=self.focus_article_enabled: self.handle_checkbutton_focus_article())
        #self.focus_article_checkbox.configure(font=("Calibri", 10, "italic"))
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()