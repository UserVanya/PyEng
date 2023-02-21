
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from pyeng_core import *
import threading
import time
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
        self._window.grid_rowconfigure(0, weight=1, minsize=40)
        self._window.grid_rowconfigure(1, weight=6, minsize=440)
        self._window.grid_rowconfigure(2, weight=1, minsize=40)
        self._window.grid_rowconfigure(3, weight=1, minsize=40)
        self._window.grid_rowconfigure(4, weight=1, minsize=40)

    def create_window(self, master, deiconify_when_closed=True):
        '''
        Creates window of translator tool and deiconfies it on exit if deiconify_when_closed is True
        '''
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
        '''
        Callback function for output scrolled text widget modification
        '''
        if event.keysym in ["Return", "Tab"]:
            last_symbol = self._output_scrolled.get("end-2c", "end-1c")
            if last_symbol in [" ", "\t", "\n"]:
                self._output_scrolled.event_generate("<BackSpace>")
            self._hint_text.focus_set()    
    def __input_scrolled_on_modify(self, event):
        '''
        Callback function for input scrolled text widget modification
        '''
        if event.keysym in ["Return", "Tab"]:
            last_symbol = self._input_scrolled.get("end-2c", "end-1c")
            if last_symbol in [" ", "\t", "\n"]:
                self._input_scrolled.event_generate("<BackSpace>")
        typed = self._input_scrolled.get("1.0", "end-1c")
        if event.keysym in ["Return", "Tab"]:
            output = self._output_scrolled.get("1.0", "end-1c")
            if typed == self._last_text_to_translate and output == self._last_translated_text:
                if event.keysym != "Tab":
                    self.__do_save() 
            elif typed != "":
                self.translate(typed)
            else:
                if event.keysym != "Tab":
                    self.__show_empty_input_error()
                self._hint_text.delete("1.0", "end")
                self._hint_text.event_generate("<FocusOut>")
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

    def __hint_text_on_modify(self, event):
        '''
        Callback function for hint text modification
        '''
        if event.keysym in ["Return", "Tab"]:
            last_symbol = self._hint_text.get("end-2c", "end-1c")
            if last_symbol in [" ", "\t", "\n"]:
                self._hint_text.event_generate("<BackSpace>")
            if event.keysym == "Tab":
                self._input_scrolled.focus_set()
            else:
                self.__do_save()    
        
    def __add_binds_to_text_widgets(self):
        '''
        Addes default parameters and bindings to text widgets
        '''
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
        
        self._hint_text.insert("1.0", "Enter hint:")
        self._hint_text.bind("<FocusIn>", lambda event: self._hint_text.delete("1.0", tk.END) if self._hint_text.get("1.0", "end-1c") == "Enter hint:" else None)
        self._hint_text.bind("<FocusOut>", lambda event: self._hint_text.insert("1.0", "Enter hint:") if self._hint_text.get("1.0", "end-1c") == "" else None)
        self._hint_text.bind("<Control-KeyPress>", ru_keys_handler)
        self._hint_text.bind("<KeyRelease>", self.__hint_text_on_modify)
    def __output_listbox_on_select(self, event):
        '''
        Callback function for output listbox modification
        '''
        self._output_scrolled.delete("1.0", "end")
        self._output_scrolled.insert("1.0", self._output_listbox.selection_get())
    def __create_text_widgets(self):
        '''
        Initializes text widgets
        '''
        self._input_scrolled = scrolledtext.ScrolledText(self._window, bg=colors["darkgrey"], fg=colors["white"], wrap="word", state='normal', undo=True)
        self._input_scrolled.grid(row=1, column=0, sticky="nsew")
        self._input_scrolled.configure(font=("Calibri", 14))

        self._output_frame = ttk.Frame(self._window, style="TFrame")
        self._output_frame.grid(row=1, column=1) #sticky="nsew")
        self._output_frame.grid_rowconfigure(0, weight=1, minsize=210)
        self._output_frame.grid_rowconfigure(1, weight=1, minsize=210)
        self._output_frame.grid_columnconfigure(0, weight=1, minsize=210)
        self._output_scrolled = scrolledtext.ScrolledText(self._output_frame, bg=colors["darkgrey"], fg=colors["lightgrey"], wrap="word", state="normal")
        self._output_scrolled.grid(row=0, column=0, sticky="nsew", rowspan=2)
        self._output_listbox = tk.Listbox(self._output_frame, bg=colors["darkgrey"], fg=colors["lightgrey"], selectmode="single") 
        #self._output_listbox.grid(row=1, column=0, sticky="nsew")
        #row=1, column=1, sticky="nsew")
        self._output_listbox.bind("<<ListboxSelect>>", self.__output_listbox_on_select)
        self._output_scrolled.configure(font=("Calibri", 14, "italic"))

        self._hint_text = tk.Text(self._window, bg=colors["darkgrey"], fg=colors["white"])
        self._hint_text.grid(row=3, column=0, sticky="nsew", columnspan=2, ipady=1)
        self._hint_text.configure(font=("Calibri", 14))
        
    def __create_lang_widgets(self):
        '''
        Initializes language widgets and also adds bindings to them
        '''
        self._langs = self._core.get_available_langs()

        self._input_lang = AutocompleteCombobox(self._window)
        self._input_lang.grid(row=2, column=0, sticky='nsew')
        self._input_lang.set_completion_list(self._langs)
        self._input_lang.bind("<FocusIn>", lambda event: self._input_lang.delete(0, tk.END) if self._input_lang.get() == "<autodetect>" else None)
        self._input_lang.bind("<FocusOut>", lambda event: self._input_lang.set("<autodetect>") if self._input_lang.get() not in self._langs else None)
        self._input_lang.bind("<Control-KeyPress>", ru_keys_handler)
        self._input_lang.insert(0, "<autodetect>")
        self._input_lang.configure(font=("Calibri", 16, "italic"))
        
        self._output_lang = AutocompleteCombobox(self._window)
        self._output_lang.set_completion_list(self._langs)
        self._output_lang.grid(row=2, column=1, sticky='nsew')
        self._output_lang.bind("<FocusIn>", lambda event: self._output_lang.delete(0, tk.END) if self._output_lang.get() not in self._langs else None)
        self._output_lang.bind("<FocusOut>", lambda event: self._output_lang.set("русский") if self._output_lang.get() not in self._langs else None)
        self._output_lang.bind("<Control-KeyPress>", ru_keys_handler)
        self._output_lang.set("русский")
        self._output_lang.configure(font=("Calibri", 16, "italic"))
    #def __service_selection_on_change(self, event):
        #self._core.set_service(self.service_combobox.get())
        #print(self.service_combobox.get())
        #self._langs = self._core.get_available_langs(self.service_combobox.get())
        #self._input_lang.set_completion_list(self._langs)
        #self._output_lang.set_completion_list(self._langs)

    def __synonims_enabled_on_change(self, s, i, m):
        #iconify output listbox
        if self._synonims_enabled.get():
            self._output_listbox.grid(row=1, column=0, sticky="nsew")
            self._output_scrolled.grid(row=0, column=0, sticky="nsew")
        else:
            self._output_listbox.grid_forget()
            self._output_scrolled.grid(row=0, column=0, sticky="nsew", rowspan=2)
    def __create_service_selection(self):
        '''
        Initializes service selection combobox
        '''
        self.service_combobox = ttk.Combobox(self._window, values=[ "Google", "Yandex"], state='readonly', justify='center', foreground=colors["black"])
        self.service_combobox.set("Yandex")
        self.service_combobox.grid(row=0, column=0, sticky='nsew')
        self.service_combobox.configure(font=("Calibri", 16))
        #self.service_combobox.bind("<<ComboboxSelected>>", self.__service_selection_on_change)

        self._synonims_enabled = tk.BooleanVar()
        self._synonims_checkbutton = ttk.Checkbutton(self._window, text='Enable synonims', variable=self._synonims_enabled, onvalue=True, offvalue=False)
        self._synonims_checkbutton.grid(row=0, column=1, sticky='nsew')
        #self._synonims_checkbutton.configure(font=("Calibri", 16))
        self._synonims_enabled.set(False)
        self._synonims_enabled.trace("w", self.__synonims_enabled_on_change)
    def is_opened(self):
        return self._is_window_opened
    
    def __create_buttons(self):
        '''
        Initializes save and translate buttons
        '''
        self._translate_button = tk.Button(self._window, text="Translate", command=self.translate, bg=colors["grey"], fg=colors["white"])
        self._translate_button.configure(font=("Calibri", 16))
        self._translate_button.grid(row=4, column=0, sticky="nsew")

        self._save_button = tk.Button(self._window, text="Add word", command=self.__do_save, bg=colors["lightgrey"], fg=colors["black"], state="disabled")
        self._save_button.configure(font=("Calibri", 16))
        self._save_button.grid(row=4, column=1, sticky="nsew")
    
    def __create_widgets(self):
        '''
        Initializes all widgets and adds bindings to them
        '''
        self.__create_service_selection()

        self.__create_text_widgets()

        self.__create_lang_widgets()

        self.__create_buttons()

        self.__add_binds_to_text_widgets()
    
    def __show_empty_input_error(self):
        '''
        Shows error message and sets focus on window
        '''
        self._window.focus_set()
        return tk.messagebox.askokcancel("Error", "Please, enter text to translate")
    def _check_and_get_corrected_input(self):
        '''
        Checks if input is empty, if so, raises the ValueError exception.
        Returns the corrected input text.
        '''
        text = self._input_scrolled.get("1.0", "end-1c")
        if text is None or text == "":
            self.__show_empty_input_error()
            raise ValueError("Input is empty")
        if text[-1] == '\n':
            text = text[:-1]
            self._input_scrolled.delete("end-1c", "end")
        text = text.strip()
        self._input_scrolled.delete("1.0", "end")
        self._input_scrolled.insert("1.0", text)
        return text
    def _check_and_get_corrected_langs(self, text):
        '''
        Detects input language and sets if <autodetec> mode is on. 
        Compares it with the language selected to translate. 
        If the languages are the same, and the language is not English, then the output language is set to 'english'. 
        If the languages are the same and the language is English, then the output language is set to 'русский'.
        '''
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
        '''
        The wrapper on do translate asynchronous function
        '''
        #print("Translation called")
        if text == "":
            try:
                text = self._check_and_get_corrected_input()
            except ValueError:
                self.__show_empty_input_error()
        if self._thread != 0:
            if not self._thread.is_alive():
                self._thread.join()
            else:
                return
        self._thread = threading.Thread(target=lambda:self._do_translate(text))
        self._thread.start()
    def _do_translate(self, text):
        '''
        Translates the text and shows the result in the output text widget
        '''
        time_start = time.time()
        try:
            lang_from_code, lang_to_code = self._check_and_get_corrected_langs(text)
            translation = self._core.get_translation(lang_from_code, lang_to_code, text, self.service_combobox.get().lower())
            if self._synonims_enabled.get():
                other_translations = self._core.get_translations(lang_from_code, lang_to_code, text)
                self._output_listbox.delete(0, tk.END)
                self._output_listbox.insert(tk.END, *other_translations)
            self._output_scrolled.delete("1.0", "end")
            self._output_scrolled.insert(tk.END, translation)
            self._last_lang_to_code = lang_to_code
            self._last_lang_from_code = lang_from_code
            self._last_text_to_translate = text
            self._last_translated_text = translation
            self._save_button.configure(state="normal")
            print(f"Translation time: {time.time() - time_start} seconds")
        except:
            tk.messagebox.askokcancel("Error", "Error occured while translating: " + str(sys.exc_info()[0]))
            return
        
    def __do_save(self):
        '''
        Saves the translation to the dictionary and shows the message box, so the focus will be on the main window
        '''
        text_out = self._output_scrolled.get("1.0", "end-1c")
        self._window.focus_set()
        answer = tk.messagebox.askokcancel("PyEng: Add word", f"Pair {self._last_text_to_translate}({self._last_lang_from_code}) - {text_out}({self._last_lang_to_code}) with hint: '{self._hint_text.get('1.0', 'end-1c')}' will be added to dictionary. Are you sure?")
        if answer:
            self._core.save_translation(self._last_lang_from_code, self._last_lang_to_code, self._last_text_to_translate, text_out)
    def add_text_to_translate(self, word):
        '''
        The function to call outside of the class to add text to the input text widget
        '''
        self._input_scrolled.delete("1.0", "end")
        self._input_scrolled.insert(tk.END, word)
    def set_focus(self):
        '''
        Sets focus on the window
        '''
        self._window.focus_set()
        self._window.focus_force()
    def close_window(self, do_master_deiconify=True):
        '''
        Closes the window and releases the focus on the master window if do_master_deiconify is True
        '''
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
