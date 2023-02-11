import tkinter as tk
from tkinter import ttk
import json
import translator_win
import os
import openpyxl
import pandas as pd
class MainApp(tk.Tk):
    def __init__(self, settings_file_path = "pyeng_settings.json"):
        super().__init__()
        self.enter_cwd()
        if not os.path.exists(settings_file_path):
            tk.messagebox.showinfo("PyEng", "Please select settings file")
            settings_file_path = tk.filedialog.askopenfilename(title="Select settings file", filetypes=[("JSON", "*.json")], parent = self)        
        self.settings_dict = json.loads(open(settings_file_path, "r").read())
        self.dict_wb_name = self.settings_dict["dict_file_name"]
        self.api_key = self.settings_dict["api_key"]
        self.folder_id = self.settings_dict["folder_id"]
        self.langs = self.settings_dict["langs"]
        self.ws_to_name = f"{self.langs[0]}_to_{self.langs[1]}"
        self.ws_from_name = f"{self.langs[1]}_to_{self.langs[0]}"
        self.init_excel_table(self.dict_wb_name, self.langs)
        self.wb = openpyxl.load_workbook(self.dict_wb_name)
        self.df_to = pd.read_excel(self.dict_wb_name, sheet_name="eng_to_rus")
        self.df_from = pd.read_excel(self.dict_wb_name, sheet_name="rus_to_eng")
        self.tr_app = translator_win.TranslatorWindow(api_key=self.api_key, 
                                                   folder_id=self.folder_id, 
                                                   langs=self.langs, 
                                                   wb=self.wb)
        
        self.create_main_window()
    def create_main_window(self):
        self.title("PyEng")
        self.geometry("1200x600")
        self.resizable(False, False)
        self.configure(bg="grey")
        self.create_widgets()
    def create_translator_window(self):
        self.tr_app.create_window( self, self.df_to, self.df_from)
    def init_excel_table(self, name, langs):
        self.enter_cwd()
        if not os.path.exists(name):
            wb = openpyxl.Workbook()
            wb['Sheet'].remove()
            if f"" not in wb.sheetnames:
              wb.create_sheet(f"{langs[0]}_to_{langs[1]}")
            if f"{langs[1]}_to_{langs[0]}" not in wb.sheetnames:
              wb.create_sheet(f"{langs[1]}_to_{langs[0]}")
            wb.save(name)
    def enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def create_widgets(self):
        self.tranlator_button = tk.Button(self.master, text="Translator", command=self.create_translator_window).pack()
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()