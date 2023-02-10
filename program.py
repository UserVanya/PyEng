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

class TranslatorApp:
    def __init__(self, master):
        
        self.colors = { "black": "#000000", "white": "#FFFFFF", "grey": "#808080", "lightgrey": "#D3D3D3", "darkgrey":"#63666A" }
        self.enter_cwd()
        settings_file_path = "pyeng_settings.json"
        if not os.path.exists(settings_file_path):
            tk.messagebox.showinfo("PyEng", "Please select settings file")
            settings_file_path = askopenfilename(title="Select settings file", filetypes=[("JSON", "*.json")], parent=master)        
        settings_dict = json.loads(open(settings_file_path, "r").read())
        self.impl = TranslatorImpl(settings_dict["api_key"],settings_dict["folder_id"], settings_dict['langs'])
        self.dict_wb_name = settings_dict['dict_file_name']
        self.init_excel_table(self.dict_wb_name)
        self.wb = openpyxl.load_workbook(self.dict_wb_name)
        self.eng_to_rus_df = pd.read_excel(self.dict_wb_name, sheet_name="eng_to_rus")
        self.rus_to_eng_df = pd.read_excel(self.dict_wb_name, sheet_name="rus_to_eng")
        self.master = master
        self.master.title("PyEng")
        self.master.geometry("1200x600")
        self.master.resizable(True, True)
        self.master.configure(bg=self.colors["white"]) 
        master.grid_columnconfigure(0, weight = 1)
        master.grid_columnconfigure(1, weight = 1)
        master.grid_rowconfigure(0, weight = 5)
        master.grid_rowconfigure(1, weight = 1)
        master.grid_rowconfigure(2, weight = 1)
        self.create_widgets()
    def get_settings_dict (self, filename):
        return json.loads(open(filename, "r").read())
    def get_current_root_geometry(self) -> dict:
        
        return self.master.winfo_geometry()
    def init_excel_table(self, name):
        self.enter_cwd()
        if not os.path.exists(name):
            wb = openpyxl.Workbook()
            wb.remove_sheet(wb.active)
            if "eng_to_rus" not in wb.sheetnames:
              wb.create_sheet("eng_to_rus")
            if "rus_to_eng" not in wb.sheetnames:
              wb.create_sheet("rus_to_eng")
            wb.save(name)
    def enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def create_widgets(self):
        self.input_scrolled = scrolledtext.ScrolledText(self.master, bg=self.colors["darkgrey"], fg=self.colors["white"], wrap="word")
        self.input_scrolled.grid(row=0, column=0, sticky="nsew")
        self.input_scrolled.bind("<Enter>", )

        self.output_scrolled = scrolledtext.ScrolledText(self.master, bg=self.colors["darkgrey"], fg=self.colors["lightgrey"], wrap="word", state="disabled")
        self.output_scrolled.grid(row=0, column=1, sticky="nsew") 

        self.detected_lang_frame = tk.Frame(self.master, bg=self.colors["black"])
        self.detected_lang_frame.grid(row=1, column=0, columnspan = 2 ,sticky="nsew")
        self.detected_lang_var = tk.StringVar()
        self.detected_lang_label = tk.Label(self.detected_lang_frame, textvariable=self.detected_lang_var, bg=self.colors["grey"], fg=self.colors["white"])
        self.detected_lang_label.pack(fill="both", expand=True)
        
        self.translate_button = tk.Button(self.master, text="Translate", command=self.translate, bg=self.colors["grey"], fg=self.colors["white"])
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
    app = TranslatorApp(root)
    root.mainloop()