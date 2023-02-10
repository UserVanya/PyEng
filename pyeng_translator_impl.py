import requests
import json
import tkinter as tk
class TranslatorImpl:
    def __init__(self, api_key, folder_id, langs):
        self.api_key = api_key
        self.folder_id = folder_id
        self.langs = langs
        self.langs_dict = {langs[0]: langs[1], langs[1]: langs[0]}
    def get_language_code(self, word: str, use_yandex_cloud = False) -> str:
        if use_yandex_cloud:
            return self.get_language_code_yacl(word)
        else:
            return self.get_language_code_simple(word)
    def get_language_code_simple(self, word: str) -> str:
        if word.isascii():
            return "en"
        else:
            return "ru"
    def get_language_code_yacl(self, word: str) -> str:
        body = {
            "folderId": self.folder_id,
            "languageCodeHints": self.langs,
            "text": word
        }
        response_dict, success, msg = self.get_response_dict("detect", body)
        if success:
            return response_dict['languageCode'], True, ""
        else:
            raise Exception(msg)
    def get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {0}".format(self.api_key)
        }
        return headers
    def get_response_dict(self, way: str, body) -> tuple:
        assert way in ["translate", "detect"]
        try:
            response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/' + way, json=body, headers=self.get_headers())
        except requests.exceptions.ConnectionError:
            return {}, False, "No internet connection"
        except requests.exceptions.Timeout:
            return {}, False, "Connection timeout"
        except requests.exceptions.HTTPError:
            return {}, False, "HTTP error"
        except requests.exceptions.RequestException:
            return {}, False, "Unknown error"
        response_dict = json.loads(response.text)
        if "code" in response_dict.keys():
            return {}, False, "Error code: {0}, message: {1}".format(response_dict['code'], response_dict['message'])
        return response_dict, True, "Success"
    
    
    
    def translate(self, word) -> tuple:
        body = {
            "targetLanguageCode": self.langs_dict[self.get_language_code(word, False)],
            "texts": word,
            "folderId": self.folder_id
        }
        response_dict, success, msg = self.get_response_dict("translate", body)
        if success:
            return response_dict['translations'][0]['text']
        else:
            raise Exception(msg)



# def main():
#     while True:
#         if keyboard.is_pressed('Ctrl + Q'):
#             try:
#                 text = pyperclip.waitForNewPaste(shortcut_timeout)
#                 print(text)
#                 translation = translate_to_rus(text)
#                 print(translation)
#                 text = pyperclip.waitForNewPaste(shortcut_timeout)
#                 tk.showinfo("Yandex Translator", translation)
#             except pyperclip.PyperclipTimeoutException:
#                 pass

def main():
    impl = TranslatorImpl("AQVNxjK5Yr282hq2cLekOt7lWu7YpMUw6KM5xiLS", "b1gf5shu9k696m00c35h")
    print(impl.translate("Hello"))

if __name__ == "__main__":
    main()    