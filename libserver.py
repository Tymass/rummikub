
libserver.py


class Message:
    def __init__(self, selector, sock, addr):
        # ...
        pass
        # ...

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
