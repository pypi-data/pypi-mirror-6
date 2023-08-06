import requests


URL = 'http://services.gingersoftware.com/Ginger/correct/json/GingerTheText'
API_KEY = '6ae0c3a0-afdc-4532-a810-82ded0054236'


class GingerIt(object):
    def __init__(self):
        self.url = URL
        self.api_key = API_KEY
        self.api_version = '2.0'
        self.lang = 'US'

    def parse(self, text):
        s = requests.Session()
        req = s.get(
            self.url,
            params={
                'lang': self.lang,
                'apiKey': self.api_key,
                'clientVersion': self.api_version,
                'text': text
            },
        )
        data = req.json()
        return self._process_data(text, data)

    @staticmethod
    def _process_data(text, data):
        result = ''
        corrections = []
        i = 0

        for suggestion in data['LightGingerTheTextResult']:
            start = suggestion["From"]
            end = suggestion["To"]

            if i <= end:
                suggest = suggestion['Suggestions'][0]
                if start != 0:
                    result += text[i:start-1]
                result += " " + suggest['Text']

                corrections.append({
                    'text': text[start:end],
                    'correct': suggest.get('Text', None),
                    'definition': suggest.get('Definition', None)
                })

            i = end + 1

        if i < len(text):
            result += text[i:-1]
        return {'text': text, 'result': result, 'corrections': corrections}
