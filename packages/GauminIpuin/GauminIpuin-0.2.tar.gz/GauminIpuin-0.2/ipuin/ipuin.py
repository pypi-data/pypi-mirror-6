from zipfile import ZipFile
from tempfile import mkstemp
import shutil
import json
import os

IPUIN_INFO_TEMPLATE = """
%(description)s

**Egilea**: *%(author)s*
"""


class Ipuin(object):
    IPUIN_DATA_TEMPLATE = {
        'title': 'ipuin berria',
        'start': 'step1',
        'author': 'ezezaguna',
        'description': 'ipuin berriaren deskribapena',
        'cover': os.path.join(os.path.dirname(__file__), 'imgs', 'empty.png'),
        'steps': {
            'step1': {
                'title': 'pausu berria',
            }
        }
    }

    def __init__(self, ipuinfile):
        self.ipuinfile = ipuinfile
        try:
            self.zipfile = ZipFile(ipuinfile)
            manifest = self.zipfile.open('MANIFEST')
            self.data = json.load(manifest)
        except IOError:
            self.zipfile = None
            self.data = self.IPUIN_DATA_TEMPLATE.copy()

        self.step = self.data['start']

        self.image_cache = {}

    def __repr__(self):
        return u"Title: %s, author: %s" % (self.title, self.author)

    @property
    def title(self):
        return self.data['title']

    @title.setter
    def title(self, value):
        self.data['title'] = value

    @property
    def cover(self):
        if self.data['cover']:
            if os.path.isabs(self.data['cover']):  # absolute paths aren't on the zip, take from the system instead
                return self.data['cover']
            else:
                return self.extract_image(self.data['cover'])
        else:
            return ''

    @cover.setter
    def cover(self, path):
        # TODO: copy path to ipuin zip
        #dirname, filename = os.path.split(path)
        if self.cover != path:  # it could be the extracted image, different path but the same image
            self.data['cover'] = path

    @property
    def description(self):
        return self.data['description']

    @description.setter
    def description(self, value):
        self.data['description'] = value

    @property
    def author(self):
        return self.data['author']

    @author.setter
    def author(self, value):
        self.data['author'] = value

    @property
    def info(self):
        return IPUIN_INFO_TEMPLATE % self.data

    @property
    def start(self):
        return self.data['start']

    @start.setter
    def start(self, value):
        if value in self.data['steps']:
            self.data['start'] = value
        else:
            raise RuntimeError('Invalid step identifier')

    @property
    def steps(self):
        return self.data['steps']

    @steps.setter
    def steps(self, value):
        self.data['steps'] = value

    def is_end_step(self, step):
        return step in self.data['endings']

    def get_step_title(self, stepname):
        return self.data['steps'][stepname]['title']

    def step_has_text(self, step):
        return 'text' in step

    def get_step_text(self, step):
        if self.step_has_text(step):
            if os.path.isabs(step['text']):  # absolute paths aren't on the zip, take from the system instead
                with open(step['text']) as textfile:
                    text = textfile.read()
            else:
                textfile = self.zipfile.open('text/' + step['text'])
                text = textfile.read()
                text = text.decode('utf-8')
            return text
        else:
            return ''

    def step_has_image(self, step):
        return 'img' in step and step['img']

    def get_step_image(self, step):
        if self.step_has_image(step):
            if os.path.isabs(step['img']):  # absolute paths aren't on the zip, take from the system instead
                return step['img']
            else:
                return self.extract_image(step['img'])
        else:
            return ''

    def get_step_targets(self, step):
        return self.data['steps'][step].get('targets', [])

    def extract_image(self, imagesrc):
        if imagesrc not in self.image_cache:
            filedescriptor, filepath = mkstemp(suffix='.' + imagesrc.split('.',)[-1])
            with open(filepath, 'wb') as targetfile:
                imgfile = self.zipfile.open('img/' + imagesrc)
                targetfile.write(imgfile.read())
                imgfile.close()
            self.image_cache[imagesrc] = filepath
        return self.image_cache[imagesrc]

    def __store_file_on_zip(self, zipfile, path, base='img/'):
        if os.path.isabs(path):
            filename = os.path.split(path)[1]
            zipfile.write(path, base + filename)
        else:
            filename = path
            data = self.zipfile.open(base + path)
            zipfile.writestr(str(base + path), data.read())
        return filename

    def save(self):
        tempzipfile = mkstemp(suffix='.ipuin')[1]
        zipfile = ZipFile(tempzipfile, 'w')

        self.data['cover'] = self.__store_file_on_zip(zipfile, self.data['cover'])
        for step in self.steps.values():
            if self.step_has_image(step):
                step['img'] = self.__store_file_on_zip(zipfile, step['img'])
            if self.step_has_text(step):
                step['text'] = self.__store_file_on_zip(zipfile, step['text'], base='text/')
        manifest = json.dumps(self.data, indent=2)
        zipfile.writestr('MANIFEST', manifest)
        zipfile.close()

        if self.zipfile is not None:
            self.zipfile.close()
        shutil.move(tempzipfile, self.ipuinfile)
        self.zipfile = ZipFile(self.ipuinfile)

    def close(self):
        if self.zipfile is not None:
            self.zipfile.close()
            self.zipfile = None
