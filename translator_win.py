import openpyxl
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import pandas as pd
import os
import json
from pyeng_translator_impl import TranslatorImpl

colors = {"darkgrey":"#6F7378", "lightgrey":"#E5E5E5", "white":"#FFFFFF", "black":"#000000", "grey":"#C0C0C0"}
'''
Translation application:
Application requires settings file in json format with the following structure:
{
    "api_key": <api_key>,
    "folder_id": <folder_id>,
    "dict_file_name": <dict_file_name>,
    "langs": [<lang1>, <lang2>, ...]
}
Application works as follows:
It contatins two text fields: one for input and one for output.
When user types in input field, application translates the word and shows the translation in output field.
'''

class TranslatorWindow:
    def __init__(self, **kwargs):
        self.enter_cwd()
        print(kwargs.items())
        self.impl = TranslatorImpl(kwargs["api_key"], kwargs["folder_id"], kwargs["langs"])
        self.wb = kwargs["wb"]
        self.df_to = pd.DataFrame()
        self.df_from = pd.DataFrame()
    def enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def dismiss(self):
        self.window.grab_release()
        self.window.destroy()
    def create_window(self, df_to, df_from):
        self.df_to = df_to
        self.df_from = df_from
        self.window = tk.Toplevel()
        self.window.title("PyEng")
        self.window.protocol("WM_DELETE_WINDOW", self.dismiss) # перехватываем нажатие на крестик
        self.window.geometry("1200x600")
        self.window.resizable(True, True)
        self.window.configure(bg=colors["darkgrey"]) 
        self.window.grid_columnconfigure(0, minsize=400, weight=1)
        self.window.grid_columnconfigure(1, minsize=400, weight=1)
        self.window.grid_rowconfigure(0, minsize=500, weight=10)
        self.window.grid_rowconfigure(1, minsize=40, weight=1)
        self.window.grid_rowconfigure(2, minsize=40, weight=1)
        self.create_widgets(self.window)
        self.window.grab_set()
    
    def create_widgets(self, window):
        self.input_scrolled = scrolledtext.ScrolledText(window, bg=colors["darkgrey"], fg=colors["white"], wrap="word")
        self.input_scrolled.grid(row=0, column=0, sticky="nsew")

        self.output_scrolled = scrolledtext.ScrolledText(window, bg=colors["darkgrey"], fg=colors["lightgrey"], wrap="word", state="disabled")
        self.output_scrolled.grid(row=0, column=1, sticky="nsew") 

        # self.detected_lang_frame = tk.Frame(self.master, bg=self.colors["black"])
        # self.detected_lang_frame.grid(row=1, column=0, columnspan = 2 ,sticky="nsew")
        self.detected_lang_var = tk.StringVar()
        self.detected_lang_label = tk.Label(window, textvariable=self.detected_lang_var, bg=colors["grey"], fg=colors["white"])
        self.detected_lang_label.grid(row=1, column=0, columnspan=2, sticky="nsew")
        #self.detected_lang_label.pack(fill="both", expand=True)
        
        self.translate_button = tk.Button(window, text="Translate", command=self.translate, bg=colors["grey"], fg=colors["white"])
        self.translate_button.grid(row=2, column=0, columnspan = 2, sticky="nsew")
    def translate(self):
        text = self.input_scrolled.get("1.0", "end-1c")
        self.detected_lang_var.set("Detected language: " + self.impl.get_language_code(text))
        self.output_scrolled.config(state="normal")
        self.output_scrolled.delete("1.0", "end")
        self.output_scrolled.insert(tk.END, self.impl.translate(text))
        self.output_scrolled.config(state="disabled")
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorWindow(root)
    root.mainloop()