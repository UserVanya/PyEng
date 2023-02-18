
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from pyeng_core import *
from autocomplete_combobox import AutocompleteCombobox
colors = {"darkgrey": "#393D47", "lightgrey": "#E5E5E5",
          "white": "#FFFFFF", "black": "#000000", "grey": "#C0C0C0"}


class TranslatorWindow:
    def __init__(self, core: PyengCore):
        self.core = core
        self.last_lang_to_code = "ru"
        self.last_lang_from_code = "en"
        self.last_text_to_translate = ""
        self.last_hint = ''
        self.is_window_opened = False
    def configure_grid(self):
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=10)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        self.window.grid_rowconfigure(4, weight=1)

    def create_window(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("PyEng")
        width = 1200
        height = 600
        center_x = int(self.master.winfo_screenwidth() / 2 - width//2)
        center_y = int(self.master.winfo_screenheight() / 2 - height//2)
        self.window.geometry(f"{width}x{height}+{center_x}+{center_y}")
        self.window.resizable(False, False)
        self.window.configure(bg=colors["darkgrey"])
        self.window.bind('<Return>', lambda event: self.do_translate())
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.bind("<Escape>", lambda event: self.close_window())
        self.configure_grid()
        self.__create_widgets()
        self.window.grab_set()
        self.is_window_opened = True
        self.window.deiconify()
        
    def __create_text_widgets(self):
        self.input_scrolled = scrolledtext.ScrolledText(self.window, bg=colors["darkgrey"], fg=colors["white"], wrap="word", state='normal')
        self.input_scrolled.grid(row=1, column=0, sticky="nsew")
        self.input_scrolled.configure(font=("Calibri", 14))
        self.text1 = "Enter text you want to translate here..."
        self.input_scrolled.insert("1.0", self.text1)
        self.input_scrolled.bind("<FocusIn>", lambda event: self.input_scrolled.delete(
            "1.0", "end") if self.input_scrolled.get("1.0", "end-1c") == self.text1 else None)
        self.input_scrolled.bind("<FocusOut>", lambda event: self.input_scrolled.insert(
            "1.0", self.text1) if self.input_scrolled.get("1.0", "end-1c") == "" else None)
        self.input_scrolled.bind("<Control-KeyPress>", ru_keys_handler)

        self.output_scrolled = scrolledtext.ScrolledText(
            self.window, bg=colors["darkgrey"], fg=colors["lightgrey"], wrap="word", state="normal")
        self.output_scrolled.grid(row=1, column=1, sticky="nsew")
        self.output_scrolled.configure(font=("Calibri", 14, "italic"))
        self.text2 = "Translation will appear here...\n(You can also change this field in order to add the appropriate translation to the dictionary)"
        self.output_scrolled.insert("1.0", self.text2)
        self.output_scrolled.bind("<Button-1>", lambda event: self.output_scrolled.delete(
            "1.0", "end") if self.output_scrolled.get("1.0", "end-1c") == self.text2 else None)
        self.output_scrolled.bind("<FocusOut>", lambda event: self.output_scrolled.insert(
            "1.0", self.text2) if self.output_scrolled.get("1.0", "end-1c") == "" else None)
        self.output_scrolled.bind("<Control-KeyPress>", ru_keys_handler)
        #self.output_scrolled.grab_set()

        self.hint_entry = tk.Entry(
            self.window, bg=colors["darkgrey"], fg=colors["white"])
        self.hint_entry.grid(
            row=3, column=0, sticky="nsew", columnspan=2, ipady=1)
        self.hint_entry.configure(font=("Calibri", 14))
        self.hint_entry.insert(0, "Enter hint:")
        self.hint_entry.bind("<Button-1>", lambda event: self.hint_entry.delete(
            0, tk.END) if self.hint_entry.get() == "Enter hint:" else None)
        self.hint_entry.bind("<FocusOut>", lambda event: self.hint_entry.insert(
            0, "Enter hint:") if self.hint_entry.get() == "" else None)

    def widget_input_lang_focus_out(self, event):
        if self.input_lang.get() == "" or self.input_lang.get() not in self.langs:
            self.input_lang.delete(0, tk.END)
            self.input_lang.insert(0, "<autodetect>")
        self.prev_input_lang = self.input_lang.get()
    def __create_lang_widgets(self):
        self.langs = self.core.get_available_langs()

        self.input_lang = AutocompleteCombobox(self.window)
        self.input_lang.grid(row=2, column=0, sticky='nsew')
        self.input_lang.set_completion_list(self.langs)
        self.input_lang.bind("<FocusIn>", lambda event: self.input_lang.delete(0, tk.END) if self.input_lang.get() == "<autodetect>" else None)
        self.input_lang.bind("<FocusOut>", self.widget_input_lang_focus_out)
        self.input_lang.bind("<Control-KeyPress>", ru_keys_handler)
        self.input_lang.insert(0, "<autodetect>")
        self.input_lang.configure(font=("Calibri", 16, "italic"))
        
        self.output_lang = AutocompleteCombobox(self.window)
        self.output_lang.set_completion_list(self.langs)
        self.output_lang.grid(row=2, column=1, sticky='nsew')
        self.output_lang.bind("<FocusIn>", lambda event: self.output_lang.delete(0, tk.END))
        self.output_lang.bind("<FocusOut>", lambda event: self.output_lang.set("русский") if self.output_lang.get() not in self.langs else None)
        self.output_lang.bind("<Control-KeyPress>", ru_keys_handler)
        self.output_lang.set("русский")
        self.output_lang.configure(font=("Calibri", 16, "italic"))

    def __create_service_selection(self):
        self.service = ttk.Combobox(self.window, values=[ "Google", "Yandex"], state='readonly', justify='center', background=colors["grey"], foreground=colors["white"])
        self.service.set("Yandex")
        self.service.grid(row=0, column=0, sticky='nsew', columnspan=2)
        self.service.configure(font=("Calibri", 16))
    def is_opened(self):
        return self.is_window_opened
    def __do_save(self):
        text_out = self.output_scrolled.get("1.0", "end-1c")
        if tk.messagebox.askokcancel("PyEng: Add word", f"Pair {self.last_text_to_translate}({self.last_lang_from_code}) - {text_out}({self.last_lang_to_code}) with hint: '{self.last_hint}' will be added to dictionary. Are you sure?"):
            self.core.save_translation(self.last_lang_from_code, self.last_lang_to_code, self.last_text_to_translate, text_out)
            self.window.focus_set()
    def __create_buttons(self):
        self.translate_button = tk.Button(self.window, text="Translate", command=self.do_translate, bg=colors["grey"], fg=colors["white"])
        self.translate_button.configure(font=("Calibri", 16))
        self.translate_button.grid(row=4, column=0, sticky="nsew")

        self.save_button = tk.Button(self.window, text="Add word", command=self.__do_save, bg=colors["lightgrey"], fg=colors["black"], state="disabled")
        self.save_button.configure(font=("Calibri", 16))
        self.save_button.grid(row=4, column=1, sticky="nsew")
    
    def __create_widgets(self):
        self.__create_service_selection()

        self.__create_text_widgets()

        self.__create_lang_widgets()

        self.__create_buttons()

    def do_translate(self):
        text = self.input_scrolled.get("1.0", "end-1c")
        if text[-1] == '\n':
            text = text[:-1]
            self.input_scrolled.delete("end-1c", "end")
        if text is None or text == "":
            tk.messagebox.showerror("Error", "Please, enter text to translate")
            return
        lang_from_code = 'en'
        detected_lang = self.core.get_detected_lang(text)
        lang_from = self.input_lang.get()
        if self.input_lang.get().startswith("<") or detected_lang != self.input_lang.get():
            lang_from = detected_lang
            self.input_lang.set(f"<detected: {lang_from}>")
        lang_from_code = self.core.get_lang_code(lang_from)
        lang_to = self.output_lang.get()
        lang_to_code = self.core.get_lang_code(lang_to)
        if lang_to_code == lang_from_code:
            if lang_to_code != "english":
                lang_to = 'english'
                lang_to_code = 'en'
                self.output_lang.set(lang_to)
            else:
                lang_to = 'русский'
                lang_to_code = 'ru'
                self.output_lang.set(lang_to)
        translation = self.core.get_translation(lang_from_code, lang_to_code, text)
        self.output_scrolled.config(state="normal")
        self.output_scrolled.delete("1.0", "end")
        self.output_scrolled.insert(tk.END, translation)
        self.last_lang_to_code = lang_to_code
        self.last_lang_from_code = lang_from_code
        self.last_text_to_translate = text
        self.last_hint = self.hint_entry.get()
        self.save_button.configure(state="normal")
    def add_text_to_translate(self, word):
        self.input_scrolled.delete("1.0", "end")
        self.input_scrolled.insert(tk.END, word)
    def set_focus(self):
        self.window.focus_set()
        self.window.focus_force()
    def close_window(self):
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.is_window_opened = False
            self.master.deiconify()
            self.master.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    core = PyengCore()
    app = TranslatorWindow(core).create_window(root)
    root.mainloop()
