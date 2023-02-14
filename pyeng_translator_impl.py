import requests
import json
import tkinter as tk


class TranslatorImpl:
    '''
    Class with methods to obtain information from yandex cloud service.
    Main methods are:
    get_language_code (word: str, hint_lang_codes: dict) -> str;
    get_translation (word: str, target_lang_code: str) ->str;
    get_available_langs () -> list;
    '''
    def __init__(self, api_key, folder_id):
        self.api_key = api_key
        self.folder_id = folder_id
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {0}".format(self.api_key)
        }
    def get_available_langs(self):
        '''
        Returns list of available languages.
        Return example:
        {
            "languages": [
                    {
                    "code": "az",
                    "name": "azərbaycan"
                    },
                    {
                    "code": "en",
                    "name": "English"
                    },
                    ...
            ]
        }
        '''
        body = {
            "folderId": self.folder_id
        }
        response_dict, success, msg = self.__get_response_dict("languages", body)
        if success:
            return response_dict['languageCode'], True, ""
        else:
            raise Exception(msg)
    def get_language_code(self, word: str, hint_lang_codes = []) -> str:
        '''
        Returns the language code for this word. 
        There are some words that can be ambiguous to determine. Hence, it is better to add some hints as a list of language codes;
        Return example:
        get_language_code("привет", 'ru')
        'ru'
        '''
        body = {
            "folderId": self.folder_id,
            "languageCodeHints": hint_lang_codes,
            "text": word
        }
        response_dict, success, msg = self.__get_response_dict("detect", body)
        if success:
            return response_dict['languageCode'], True, ""
        else:
            raise Exception(msg)
    def get_translation(self, word, hint_lang_codes = ['en', 'ru'], target_lang_code = 'en') -> dict:
        '''
        Returns the translation of the given word (with the detected language code) 
        into the language with target_lang_code (default: 'en')
        Return example:
        get_translation ("Hello", 'en')
        {
            "text": "Привет",
            "detectedLanguageCode": "en"
        }
        '''
        body = {
            "targetLanguageCode": target_lang_code,
            "texts": word,
            "folderId": self.folder_id,
            "languageCodeHints": hint_lang_codes,
        }
        response_dict, success, msg = self.__get_response_dict("translate", body)
        if success:
            return response_dict['translations'][0]
        else:
            raise Exception(msg)
    def __get_response_dict(self, request_string: str, body) -> tuple:
        assert request_string in ["translate", "detect", 'languages']
        try:
            response = requests.post(
                'https://translate.api.cloud.yandex.net/translate/v2/' + request_string, json=body, headers=self.headers)
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

def main():
    impl = TranslatorImpl("AQVNxjK5Yr282hq2cLekOt7lWu7YpMUw6KM5xiLS", "b1gf5shu9k696m00c35h")
    print(impl.get_translation("Hello", 'ru'))
    print(impl.get_language_code("Hello", ['ru', 'en']))
    print(impl.get_available_langs())

if __name__ == "__main__":
    main()    