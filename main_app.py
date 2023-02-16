import tkinter as tk
from tkinter import ttk
import json
import os
import openpyxl
import pandas as pd
from pyeng_translator_win import TranslatorWindow
from pyeng_core import PyengCore
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.core = PyengCore()
        self.enter_cwd()
        self.create_main_window()
    def create_main_window(self):
        self.title("PyEng")
        self.geometry("1200x600")
        self.resizable(False, False)
        self.configure(bg="grey")
        self.create_widgets()
    def create_translator_window(self):
        self.tr_app = TranslatorWindow(self.core).create_window(self)
    def enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def create_widgets(self):
        self.tranlator_button = tk.Button(self.master, text="Translator", command=self.create_translator_window).pack()
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()