from langdetect import detect
from langcodes import Language
import requests
import json

class Translator:

    def __init__(self):
        self.libre_url = None
        self.headers = {'Content-Type': 'application/json'}

    def set_libre_url(self, url):
        self.libre_url = url

    def get_language_code(self, text):
        return detect(text)

    def get_language(self, language_code):
        return Language.get(language_code)

    def translate(self, message, from_lang_code, to_lang_code):
        json_request = {}
        json_request["q"] = message
        json_request["source"] = from_lang_code
        json_request["target"] = to_lang_code
        response = requests.post(self.libre_url, headers=self.headers, data=json.dumps(json_request))
        response.raise_for_status()
        translated_data = response.json()
        if ("error" in translated_data):
            raise Exception(translated_data["error"])
        return translated_data['translatedText']


