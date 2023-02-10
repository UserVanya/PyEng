import openpyxl
import tkinter as tk
import os
'''
Translation application
'''

class TranslatorApp:
    def __init__(self, master):
        self.init_excel_table()
        self.wb_name = "words.xlsx"
        self.wb = openpyxl.load_workbook(self.wb_name)
        self.master = master
        self.master.title("Yandex Translator")
        self.master.geometry("300x300")
        self.master.resizable(True, True)
        self.master.configure(bg="#f0f0f0")
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.create_widgets()
    def init_excel_table(self):
        self.enter_cwd()
        if not os.path.exists("words.xlsx"):
            wb = openpyxl.Workbook()
            if "eng_to_rus" not in wb.sheetnames:
              wb.create_sheet("eng_to_rus")
            if "rus_to_eng" not in wb.sheetnames:
              wb.create_sheet("rus_to_eng")
            wb.save("words.xlsx")
    def enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def create_widgets(self):
        self.text = tk.Text(self.master, bg="#f0f0f0", fg="#000000", font=("Arial", 12), width=30, height=10)
        self.text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.button = tk.Button(self.master, text="Translate", bg="#f0f0f0", fg="#000000", font=("Arial", 12), command=self.translate)
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    def translate(self):
        text = self.text.get("1.0", "end-1c")
        print(text)
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()