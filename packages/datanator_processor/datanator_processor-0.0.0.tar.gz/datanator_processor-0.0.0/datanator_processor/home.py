from process.incident import Incident
from process.mlstripper import strip_tags
import json
import os
import sys


class Home():
    def __init__(self):
        if '-test' in sys.argv:
            self.testing = True
        else:
            self.testing = False

        if '-verbose' in sys.argv:
            self.verbose = True
        else:
            self.verbose = False

        self.incidents = []

        for file in os.listdir('../src/json/'):
            self.output = {}
            if file.endswith('.json'):
                if self.testing:
                    print('processing file test', file)
                with open('../src/json/' + file, 'r') as active_file:
                    for line in active_file.readlines():
                        line = json.loads(line)
                        if self.testing:
                            try:
                                print(
                                    'processing line test',
                                    file,
                                    ':\n',
                                    json.dumps(line, indent=4, sort_keys=True)
                                )
                            except(UnicodeEncodeError):
                                print(
                                    'Warning: processing line test error:',
                                    sys.exc_info()[0]
                                )

                            self.incidents.append(Incident(self, file, line))
                        else:
                            self.incidents.append(Incident(self, file, line))

                if self.testing:
                    print('Just testing, so no moving source files')
                else:
                    os.rename(
                        '../src/json/' + file,
                        '../src/json/processed/' + file
                    )

            if self.testing:
                print('Just testing, so no saving output files')
            else:
                with open('../src/processed/' + file, 'w') as file:
                    json.dump(self.output, file)

    def betwixt(self, text, begin, end, start=0):
        results = []
        while start < len(text):
            start = text.find(begin, start)
            if start == -1:
                break
            start += len(begin)
            stop = text.find(end, start)
            results.append(text[start:stop])
        return results

    def betwixt_tags(self, text, begin, end, start=0):
        results = []
        while start < len(text):
            start = text.find(begin, start)
            if start == -1:
                break
            stop = text.find(end, start)
            results.append(text[start:stop + len(end)])
            start += len(begin)
        return results

    def clean(self, text):
        if text is None:
            return ''
        else:
            text = text.replace('\t', '')
            text = text.replace('\n', '')
            text = text.replace('\r', '')
            text = text.replace('  ', '')
            junk = text.find('Read the full article:')
            text = text[:junk]
            return strip_tags(text)

    def exit(self):
        pass
