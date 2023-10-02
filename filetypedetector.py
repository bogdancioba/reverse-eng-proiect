import os
import detmap
from detmap import Detection
from enum import Enum
import chardet
import nltk
from nltk.corpus import stopwords
import langdetect
import random
import re
import zipfile
from io import BytesIO
from pptx import Presentation
from pyxlsb import open_workbook as open_xlsb


#nltk.download('stopwords')

class FileTypeDetector:
    def __init__(self):
        self.detmap = detmap.Detection

    def init(self):
        return True

    def scan(self, path):
        detections = set()
        
        with open(path, 'rb') as file:
            data = file.read()

        if self.is_binary(data):
            detections.add(Detection.Binary)
        else:
            if self.is_utf8(data):
                detections.add(Detection.UTF8)
            if self.is_text(data):
                detections.add(Detection.Text)

        if self.is_unicode(data):
            detections.add(self.detmap.Unicode)

        if self.is_utf8(data):
            detections.add(self.detmap.UTF8)

        if self.is_python_bytecode(data):
            detections.add(self.detmap.PythonBytecode)

        if self.is_text(data):
            detections.add(self.detmap.Text)

        if self.is_english(data):
            detections.add(self.detmap.LanguageEnglish)

        if self.is_romanian(data):
            detections.add(self.detmap.LanguageRomanian)

        if self.is_python_script(data):
            detections.add(self.detmap.PythonScript)

        if self.is_png(data):
            detections.add(self.detmap.MediaImage)
            detections.add(self.detmap.Binary)

        if self.is_zip(data):
            detections.add(self.detmap.ZipArchive)
            detections.add(self.detmap.Binary)

        if self.is_link_document(data):
            detections.add(self.detmap.LinkDocument)

        if self.is_secret_document(data):
            detections.add(self.detmap.SecretDocument)
        
        if self.contains_image(data):
            detections.add(self.detmap.ImagesInDocument)

        if self.contains_macros(data):
            detections.add(self.detmap.MacrosInDocument)

        if self.contains_xml_macros(data):
            detections.add(self.detmap.XMLMacrosDocument)

        if self.is_pptx(data):
            detections.add(self.detmap.PttxFile)
            detections.add(self.detmap.Binary)

        if self.is_xlsb(data):
            detections.add(self.detmap.XLSBFile)
            detections.add(self.detmap.Binary)




        print("Detected: " + str(detections))
        return detections

    def uninit(self):
        pass

    def is_utf8(self, data):
        try:
            data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False

    def is_python_script(self, data):
        try:
            decoded_data = data.decode('utf-8')
            if decoded_data.startswith('#!') and 'python' in decoded_data.splitlines()[0]:
                return True
            if decoded_data.strip().startswith("import") or decoded_data.strip().startswith("from"):
                return True
        except UnicodeDecodeError:
            pass
        return False
    
    def is_binary(self, data):
        textchars = bytes({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        return bool(data.translate(None, textchars))

    def is_python_bytecode(self, data):
        if len(data) < 4:
            return False
        magic_number = data[:4]
        return magic_number in {b'\x16\r\r\n', b'\x17\r\r\n', b'\x18\r\r\n', b'\x19\r\r\n', b'\x1a\r\r\n'}
    
    def is_text(self, data):
        result = chardet.detect(data)
        confidence = result["confidence"]
        encoding = result["encoding"]

        if confidence > 0.95 and (encoding.startswith("utf") or encoding.startswith("iso") or encoding.startswith("ascii")):
            return True
        return False

    def is_unicode(self, data):
        if self.is_utf8(data):
            return False

        try:
            data.decode('utf-16')
            return True
        except UnicodeDecodeError:
            pass

        try:
            data.decode('utf-32')
            return True
        except UnicodeDecodeError:
            pass

        return False

    def is_english(self, data):
        try:
            decoded_data = data.decode('utf-8')
            sample_text = self.sample_text(decoded_data)
            detected_language = langdetect.detect(sample_text)
            return detected_language == 'en'
        except (UnicodeDecodeError, langdetect.lang_detect_exception.LangDetectException):
            pass
        return False

    def is_romanian(self, data):
        try:
            decoded_data = data.decode('utf-8')
            sample_text = self.sample_text(decoded_data)
            detected_language = langdetect.detect(sample_text)
            return detected_language == 'ro'
        except (UnicodeDecodeError, langdetect.lang_detect_exception.LangDetectException):
            pass
        return False

    def is_png(self, data):
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return True
        return False

    def is_zip(self, data):
        if data[:4] == b'PK\x03\x04':
            return True
        return False
    
    def is_link_document(self, data):
        try:
            decoded_data = data.decode('utf-8')
            if 'http://' in decoded_data or 'https://' in decoded_data:
                return True
        except UnicodeDecodeError:
            pass
        return False

    def is_secret_document(self, data):
        try:
            decoded_data = data.decode('utf-8')
            if 'secret' in decoded_data:
                return True
        except UnicodeDecodeError:
            pass
        return False


    def is_jpeg(self, data):
        if data.startswith(b'\xFF\xD8') and data.endswith(b'\xFF\xD9'):
            return True
        return False

    def contains_image(self, data):
        return self.is_jpeg(data) or self.is_png(data)

    def contains_macros(self, data):
        if self.is_zip(data):
            try:
                with zipfile.ZipFile(BytesIO(data)) as zfile:
                    for name in zfile.namelist():
                        if name.startswith('word/vbaProject.bin'):
                            return True
            except zipfile.BadZipFile:
                pass
        return False

    def contains_xml_macros(self, data):
        if self.is_zip(data):
            try:
                with zipfile.ZipFile(BytesIO(data)) as zfile:
                    for name in zfile.namelist():
                        if re.search(r'word/_rels/vbaProject.bin.rels', name):
                            return True
            except zipfile.BadZipFile:
                pass
        return False


    def sample_text(self, text, sample_size=100):
        words = text.split()
        if len(words) > sample_size:
            words = random.sample(words, sample_size)
        return ' '.join(words)
    
    def is_pptx(self, data):
        try:
            pptx.Presentation(BytesIO(data))
            return True
        except:
            return False

    def is_xlsb(self, data):
        try:
            xlsb.Book(BytesIO(data))
            return True
        except:
            return False
