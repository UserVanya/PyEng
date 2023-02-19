import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from pyeng_translator_win import TranslatorWindow
from pyeng_core import PyengCore
import keyboard
import pyperclip
colors = {"darkgrey": "#393D47", "lightgrey": "#E5E5E5",
          "white": "#FFFFFF", "black": "#000000", "grey": "#C0C0C0"}
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._core = PyengCore()
        self._enter_cwd()
        self._tr_app = TranslatorWindow(self._core)
        self.option_add("*Font", ("Calibri", 20, "bold"))
        self._configure_main_window()
        self.thread = 0
    def set_default_focus(self):
        self._tranlator_button.focus_set()
    def _translator_callback(self, event=None):
        if not self._tr_app.is_opened():
            self._tr_app.create_window(self)
        self._tr_app.set_focus()
        text = pyperclip.paste().replace("\n", " ").replace(chr(2), "")
        self._tr_app.add_text_to_translate(text)
        self._tr_app.translate()
        #self.do_translate()
        #time.sleep(0.5)
    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
    def keys_handler(self, event):
        if event.keysym == 'Escape':
            self.iconify()
        elif event.keysym == 'Return':
            self.focus_get().invoke()
        elif event.keysym == 'Up':
            self.event_generate("<Shift-Tab>")
        elif event.keysym == 'Down':
            self.event_generate("<Tab>")

    def _configure_main_window(self):
        self.title("PyEng")
        width = 800
        height = 600
        center_x = int(self.winfo_screenwidth() / 2 - width//2)
        center_y = int(self.winfo_screenheight() / 2 - height//2)
        self.geometry(f"{width}x{height}+{center_x}+{center_y}")
        self.resizable(True, True)
        self.configure(bg=colors["darkgrey"])
        self._configure_grid()
        self._create_widgets()
        self.bind("<KeyRelease>", self.keys_handler)
        self.set_default_focus()
    def _create_translator_window(self):
        self._tr_app.create_window(self)
        #hide main window
        self.iconify()
    def _enter_cwd(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    def _create_learn_window(self):
        pass
    def _create_dictionary_window(self):
        pass    
    def _create_translate_from_file_window(self):
        pass
    def _handle_checkbutton_inline_translations(self):
        if self._inline_translations_enabled.get():
            self._hotkey_inline_translations = keyboard.add_hotkey('ctrl+q', self._translator_callback)
            keyboard.add_hotkey('escape', lambda: self._tr_app.close_window(False))
        else:
            keyboard.remove_hotkey(self._hotkey_inline_translations)
    def _create_widgets(self):
        self._tranlator_button = tk.Button(self, text="Translator", command=self._create_translator_window, bg=colors["black"], fg=colors["white"])
        self._tranlator_button.grid(row=0, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        
        self._learn_button = tk.Button(self, text="Learn", command=self._create_learn_window, bg=colors["black"], fg=colors["white"])
        self._learn_button.grid(row=1, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        
        self._dictionary_button = tk.Button(self, text="Dictionary", command=self._create_dictionary_window, bg=colors["black"], fg=colors["white"])
        self._dictionary_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        
        self._translate_from_file_button = tk.Button(self, text="Translate from file", command=self._create_translate_from_file_window, bg=colors["black"], fg=colors["white"])
        self._translate_from_file_button.grid(row=3, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        
        self._inline_translations_enabled = tk.BooleanVar()
        self._inline_translations_checkbox = ttk.Checkbutton(self, text="Inline translations (Press <Ctrl-C> on text you want to translate and then <Ctrl-Q> to open translator window)", variable=self._inline_translations_enabled, onvalue=True, offvalue=False)
        self._inline_translations_checkbox.grid(row=4, column=1, sticky="e", padx=5, pady=5)
        self._inline_translations_enabled.trace("w", lambda name, index, mode, sv=self._inline_translations_enabled: self._handle_checkbutton_inline_translations())
def main():
    app = MainApp()
    app.mainloop()
if __name__ == "__main__":
    main()