from process.dataset.isaalab import Isaalab
import json
import requests
import sys


class Incident():
    def __init__(self, home, name, source):
        self.home = home
        self.name = name
        self.source = source
        self.datasets = {}

        self.fields = self.source
        self.fields['datasets'] = {}

        if self.fields['source'] == 'Kimono':
            self.text = self.fields['summary']
        else:
            self.text = self.scrape(self.source['url'])

        if self.home.testing:
            print('Test is:\n', self.text)

        self.lower_text = self.text.lower()

        self.datasets['isaalab'] = Isaalab(self)

        self.home.output[self.source['source_id']] = self.fields

    def scrape(self, url):
        try:
            text = requests.get(url).text
        except:
            print('Warning: scrape did not like something:', sys.exc_info()[0])
            return ''
        ps = self.home.betwixt(text, '<p>', '</p>')
        text = ' '.join(ps)
        text = self.home.clean(text)
        return text

