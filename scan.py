import detmap
from filetypedetector import FileTypeDetector

class MyScanner:
    def init(self):
        self.detector = FileTypeDetector()
        return self.detector.init()
    
    def scan(self, path):
        return self.detector.scan(path)
    
    def uninit(self):
        self.detector.uninit()
