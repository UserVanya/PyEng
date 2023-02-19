
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from pyeng_core import *
import threading
from autocomplete_combobox import AutocompleteCombobox
colors = {"darkgrey": "#393D47", "lightgrey": "#E5E5E5",
          "white": "#FFFFFF", "black": "#000000", "grey": "#C0C0C0"}


class TranslatorWindow:
    def __init__(self, core: PyengCore):
        self._core = core
        self._is_window_opened = False
        self.__init_defaults()
        self._thread = 0
    def __init_defaults(self):
        '''
        Initialize default values for variables last_lang_to_code, last_lang_from_code, last_text_to_translate, last_hint
        '''
        self._last_lang_to_code = "ru"
        self._last_lang_from_code = "en"
        self._last_text_to_translate = ""
        self._last_translated_text = ""
        #self._last_hint = ''
    def __configure_grid(self):
        '''
        Configures grid for window
        '''
        self._window.grid_columnconfigure(0, weight=1)
        self._window.grid_columnconfigure(1, weight=1)
        self._window.grid_rowconfigure(0, weight=1)
        self._window.grid_rowconfigure(1, weight=10)
        self._window.grid_rowconfigure(2, weight=1)
        self._window.grid_rowconfigure(3, weight=1)
        self._window.grid_rowconfigure(4, weight=1)

    def create_window(self, master, deiconify_when_closed=True):
        self._master = master
        self.__init_defaults()
        self._window = tk.Toplevel(master)
        self._window.title("PyEng")
        width = 1200
        height = 600
        center_x = int(self._master.winfo_screenwidth() / 2 - width//2)
        center_y = int(self._master.winfo_screenheight() / 2 - height//2)
        self._window.geometry(f"{width}x{height}+{center_x}+{center_y}")
        self._window.resizable(False, False)
        self._window.configure(bg=colors["darkgrey"])
        self._window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(deiconify_when_closed))
        self.__configure_grid()
        self.__create_widgets()
        self._window.grab_set()
        self._is_window_opened = True
        self._input_scrolled.focus_set()
        self._window.deiconify()
    def __output_scrolled_on_modify(self, event):
        if event.keysym in ["Return", "Tab"]:
            self._output_scrolled.event_generate("<BackSpace>")
            if event.keysym == "Tab":
                self._hint_entry.focus_set()    
    def __input_scrolled_on_modify(self, event):
        print("hello")
        typed = ""
        if event.keysym in ["Return", "Tab"]:
            self._input_scrolled.event_generate("<BackSpace>")
        typed = self._input_scrolled.get("1.0", "end-1c")
        if event.keysym in ["Return", "Tab"]:
            print(typed)
            output = self._output_scrolled.get("1.0", "end-1c")
            if typed == self._last_text_to_translate and output == self._last_translated_text:
                if event.keysym != "Tab":
                    self.__do_save() 
            elif typed != "":
                print("|" + typed + "|")
                self.translate(typed)
            else:
                if event.keysym != "Tab":
                    self.__show_empty_input_error()
                self._hint_entry.delete(0, "end")
                self._hint_entry.event_generate("<FocusOut>")
                self._output_scrolled.delete("1.0", "end")
                self._output_scrolled.event_generate("<FocusOut>")
            if event.keysym == "Tab":
                #self._input_scrolled.event_generate("<FocusOut>")
                self._output_scrolled.focus_set()
                return
        if event.keysym == "Escape":
           self.close_window()
           return 
        if typed == self._last_text_to_translate:
            self._save_button.configure(state="normal")
        else:
            self._save_button.configure(state="disabled")
            
            #print("unbinding <Return> and binding <Return> to save")
    # def __hint_entry_on_modify(self, event):
    #     print(event.keysym)
    #     self._input_scrolled.grab_set()
    #     self._input_scrolled.focus_set()
    #     if event.keysym == "Tab":
    #         print("here2")
    #         #self._input_scrolled.focus_force()
    #         #self._input_scrolled. 
    #     else:
    #         pass
    def __add_binds_to_text_widgets(self):
        self.text1 = "Enter text you want to translate here..."
        self._input_scrolled.insert("1.0", self.text1)
        self._input_scrolled.bind("<FocusIn>", lambda event: self._input_scrolled.delete("1.0", "end") if self._input_scrolled.get("1.0", "end-1c") == self.text1 else None)
        self._input_scrolled.bind("<FocusOut>", lambda event: self._input_scrolled.insert("1.0", self.text1) if self._input_scrolled.get("1.0", "end-1c") == "" else None)
        self._input_scrolled.bind("<Control-KeyPress>", ru_keys_handler)
        #deactivate add text button on any change of _input_scrolled
        self._input_scrolled.bind("<KeyRelease>", self.__input_scrolled_on_modify )


        self.text2 = "Translation will appear here...\n(You can also change this field in order to add the appropriate translation to the dictionary)"
        self._output_scrolled.insert("1.0", self.text2)
        self._output_scrolled.bind("<FocusIn>", lambda event: self._output_scrolled.delete("1.0", "end") if self._output_scrolled.get("1.0", "end-1c") == self.text2 else None)
        self._output_scrolled.bind("<FocusOut>", lambda event: self._output_scrolled.insert("1.0", self.text2) if self._output_scrolled.get("1.0", "end-1c") == "" else None)
        self._output_scrolled.bind("<Control-KeyPress>", ru_keys_handler)
        self._output_scrolled.bind("<KeyRelease>", self.__output_scrolled_on_modify )
        
        self._hint_entry.insert(0, "Enter hint:")
        self._hint_entry.bind("<FocusIn>", lambda event: self._hint_entry.delete(0, tk.END) if self._hint_entry.get() == "Enter hint:" else None)
        self._hint_entry.bind("<FocusOut>", lambda event: self._hint_entry.insert(0, "Enter hint:") if self._hint_entry.get() == "" else None)
        self._hint_entry.bind("<Control-KeyPress>", ru_keys_handler)
        #self._hint_entry.bind("<Key>", self.__hint_entry_on_modify)
        
    def __create_text_widgets(self):
        self._input_scrolled = scrolledtext.ScrolledText(self._window, bg=colors["darkgrey"], fg=colors["white"], wrap="word", state='normal', undo=True)
        self._input_scrolled.grid(row=1, column=0, sticky="nsew")
        self._input_scrolled.configure(font=("Calibri", 14))

        self._output_scrolled = scrolledtext.ScrolledText(self._window, bg=colors["darkgrey"], fg=colors["lightgrey"], wrap="word", state="normal")
        self._output_scrolled.grid(row=1, column=1, sticky="nsew")
        self._output_scrolled.configure(font=("Calibri", 14, "italic"))

        self._hint_entry = tk.Entry(self._window, bg=colors["darkgrey"], fg=colors["white"])
        self._hint_entry.grid(row=3, column=0, sticky="nsew", columnspan=2, ipady=1)
        self._hint_entry.configure(font=("Calibri", 14))
        
    def __create_lang_widgets(self):
        self.langs = self._core.get_available_langs()

        self._input_lang = AutocompleteCombobox(self._window)
        self._input_lang.grid(row=2, column=0, sticky='nsew')
        self._input_lang.set_completion_list(self.langs)
        self._input_lang.bind("<FocusIn>", lambda event: self._input_lang.delete(0, tk.END) if self._input_lang.get() == "<autodetect>" else None)
        self._input_lang.bind("<FocusOut>", lambda event: self._input_lang.set("<autodetect>") if self._input_lang.get() not in self.langs else None)
        self._input_lang.bind("<Control-KeyPress>", ru_keys_handler)
        self._input_lang.insert(0, "<autodetect>")
        self._input_lang.configure(font=("Calibri", 16, "italic"))
        
        self._output_lang = AutocompleteCombobox(self._window)
        self._output_lang.set_completion_list(self.langs)
        self._output_lang.grid(row=2, column=1, sticky='nsew')
        self._output_lang.bind("<FocusIn>", lambda event: self._output_lang.delete(0, tk.END) if self._output_lang.get() not in self.langs else None)
        self._output_lang.bind("<FocusOut>", lambda event: self._output_lang.set("русский") if self._output_lang.get() not in self.langs else None)
        self._output_lang.bind("<Control-KeyPress>", ru_keys_handler)
        self._output_lang.set("русский")
        self._output_lang.configure(font=("Calibri", 16, "italic"))

    def __create_service_selection(self):
        self.service_combobox = ttk.Combobox(self._window, values=[ "Google", "Yandex"], state='readonly', justify='center', foreground=colors["black"])
        self.service_combobox.set("Yandex")
        self.service_combobox.grid(row=0, column=0, sticky='nsew', columnspan=2)
        self.service_combobox.configure(font=("Calibri", 16))
    
    def is_opened(self):
        return self._is_window_opened
    
    def __create_buttons(self):
        self._translate_button = tk.Button(self._window, text="Translate", command=self.translate, bg=colors["grey"], fg=colors["white"])
        self._translate_button.configure(font=("Calibri", 16))
        self._translate_button.grid(row=4, column=0, sticky="nsew")

        self._save_button = tk.Button(self._window, text="Add word", command=self.__do_save, bg=colors["lightgrey"], fg=colors["black"], state="disabled")
        self._save_button.configure(font=("Calibri", 16))
        self._save_button.grid(row=4, column=1, sticky="nsew")
    
    def __create_widgets(self):
        self.__create_service_selection()

        self.__create_text_widgets()

        self.__create_lang_widgets()

        self.__create_buttons()

        self.__add_binds_to_text_widgets()
    
    def __show_empty_input_error(self):
        self._window.focus_set()
        tk.messagebox.askokcancel("Error", "Please, enter text to translate")
    def _check_and_get_corrected_input(self):
        text = self._input_scrolled.get("1.0", "end-1c")
        if text is None or text == "":
            self.__show_empty_input_error()
            return
        if text[-1] == '\n':
            text = text[:-1]
            self._input_scrolled.delete("end-1c", "end")
        text = text.strip()
        self._input_scrolled.delete("1.0", "end")
        self._input_scrolled.insert("1.0", text)
        return text
    def _check_and_get_corrected_langs(self, text):
        lang_from_code = 'en'
        detected_lang = self._core.get_detected_lang(text)
        lang_from = self._input_lang.get()
        if self._input_lang.get().startswith("<") or detected_lang != self._input_lang.get():
            lang_from = detected_lang
            self._input_lang.set(f"<detected: {lang_from}>")
        lang_from_code = self._core.get_lang_code(lang_from)
        lang_to = self._output_lang.get()
        lang_to_code = self._core.get_lang_code(lang_to)
        if lang_to_code == lang_from_code:
            if lang_to_code != "english":
                lang_to = 'english'
                lang_to_code = 'en'
                self._output_lang.set(lang_to)
            else:
                lang_to = 'русский'
                lang_to_code = 'ru'
                self._output_lang.set(lang_to)
        return lang_from_code, lang_to_code
    def translate(self, text=""):
        print("Translation called")
        if text == "":
            text = self._check_and_get_corrected_input()
        if self._thread != 0:
            if not self._thread.is_alive():
                self._thread.join()
            else:
                return
        self._thread = threading.Thread(target=lambda:self._do_translate(text))
        self._thread.start()
    def _do_translate(self, text):
        try:
            lang_from_code, lang_to_code = self._check_and_get_corrected_langs(text)
            translation = self._core.get_translation(lang_from_code, lang_to_code, text)
            self._output_scrolled.delete("1.0", "end")
            self._output_scrolled.insert(tk.END, translation)
            self._last_lang_to_code = lang_to_code
            self._last_lang_from_code = lang_from_code
            self._last_text_to_translate = text
            self._last_translated_text = translation
            self._save_button.configure(state="normal")
        except:
            tk.messagebox.askokcancel("Error", "Error occured while translating: " + str(sys.exc_info()[0]))
            return
        
    def __do_save(self):
        text_out = self._output_scrolled.get("1.0", "end-1c")
        self._window.focus_set()
        answer = tk.messagebox.askokcancel("PyEng: Add word", f"Pair {self._last_text_to_translate}({self._last_lang_from_code}) - {text_out}({self._last_lang_to_code}) with hint: '{self._hint_entry.get()}' will be added to dictionary. Are you sure?")
        if answer:
            self._core.save_translation(self._last_lang_from_code, self._last_lang_to_code, self._last_text_to_translate, text_out)
    def add_text_to_translate(self, word):
        self._input_scrolled.delete("1.0", "end")
        self._input_scrolled.insert(tk.END, word)
    def set_focus(self):
        self._window.focus_set()
        self._window.focus_force()
    def close_window(self, do_master_deiconify=True):
        if self._window and self._is_window_opened:
            self._window.grab_release()
            self._window.destroy()
            self._is_window_opened = False
            if (do_master_deiconify):
                self._master.deiconify()
                self._master.set_default_focus()

if __name__ == "__main__":
    root = tk.Tk()
    core = PyengCore()
    app = TranslatorWindow(core).create_window(root)
    root.mainloop()
