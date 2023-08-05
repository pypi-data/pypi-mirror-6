import sys


class DisabledStderr():
    def __enter__(self):
        self.stderr = sys.stderr
        sys.stderr = None
    
    def __exit__(self, type, value, traceback):
        sys.stderr = self.stderr
