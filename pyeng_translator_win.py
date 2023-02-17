import openpyxl
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import pandas as pd
import os
import json
from pyeng_core import PyengCore

colors = {"darkgrey":"#393D47", "lightgrey":"#E5E5E5", "white":"#FFFFFF", "black":"#000000", "grey":"#C0C0C0"}

class TranslatorWindow:
    def __init__(self, core: PyengCore):
        self.core = core
    def configure_grid(self):
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=10)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
    def create_window(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("PyEng")
        self.window.geometry("1200x600")
        self.window.resizable(False, False)
        self.window.configure(bg=colors["darkgrey"]) 
        self.configure_grid()
        self.create_widgets()
    
    def create_text_widgets(self):
        self.input_scrolled = scrolledtext.ScrolledText(self.window, bg=colors["darkgrey"], fg=colors["white"], wrap="word")
        self.input_scrolled.grid(row=1, column=0, sticky="nsew")
        self.input_scrolled.configure(font=("Calibri", 14))

        self.output_scrolled = scrolledtext.ScrolledText(self.window, bg=colors["darkgrey"], fg=colors["lightgrey"], wrap="word", state="disabled")
        self.output_scrolled.grid(row=1, column=1, sticky="nsew") 
        self.output_scrolled.configure(font=("Calibri", 14, "italic"))

    def create_lang_widgets(self):
        self.langs = self.core.get_available_langs()
        
        self.input_lang = ttk.Combobox(self.window, values=self.langs, state='readonly')
        self.input_lang.set("<autodetect>")
        self.input_lang.grid(row=2, column=0, sticky='nsew')
        self.input_lang.configure(font=("Calibri", 16, "italic"))
        
        self.output_lang = ttk.Combobox(self.window, values=self.langs, state='readonly')
        self.output_lang.set("русский")
        self.output_lang.grid(row=2, column=1, sticky='nsew')
        self.output_lang.configure(font=("Calibri", 16, "italic"))
        
    def create_service_selection(self):
        self.service = ttk.Combobox(self.window, values=["Google", "Yandex"], state='readonly', justify='center', background=colors["grey"], foreground=colors["white"])
        self.service.set("Google")
        self.service.grid(row=0, column=0, sticky='nsew', columnspan = 2)
        self.service.configure(font=("Calibri", 16))
    def save(self):
        params = self.translate()
        self.core.save_translation(params[0], params[1], params[2], params[3])
    def create_buttons(self):
        self.translate_button = tk.Button(self.window, text="Translate", command=self.translate, bg=colors["grey"], fg=colors["white"])
        self.translate_button.configure(font=("Calibri", 16))
        self.translate_button.grid(row=3, column=0, sticky="nsew")

        self.save_button = tk.Button(self.window, text="Add word", command=self.save, bg=colors["lightgrey"], fg=colors["black"])
        self.save_button.configure(font=("Calibri", 16))
        self.save_button.grid(row=3, column=1, sticky="nsew")

    def create_widgets(self):
        self.create_service_selection()

        self.create_text_widgets()

        self.create_lang_widgets()

        self.create_buttons()

    def translate(self):
        text = self.input_scrolled.get("1.0", "end-1c")
        lang_from_code = 'en'
        if self.input_lang.get().startswith("<"):
            lang_from = self.core.get_detected_lang(text)
            lang_from_code = self.core.get_lang_code(lang_from)
            self.input_lang.set(f"<detected: {lang_from}>")
        lang_to = self.output_lang.get()
        lang_to_code = self.core.get_lang_code(lang_to)
        translation = self.core.get_translation(lang_from_code, lang_to_code, text)
        self.output_scrolled.config(state="normal")
        self.output_scrolled.delete("1.0", "end")
        self.output_scrolled.insert(tk.END, translation)
        self.output_scrolled.config(state="disabled")
        return lang_from_code, lang_to_code, text, translation
if __name__ == "__main__":
    root = tk.Tk()
    core = PyengCore()
    app = TranslatorWindow(core).create_window(root)
    root.mainloop()