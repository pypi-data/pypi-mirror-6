class FlashFactory:

    # XXX: Is there any point in creating a per-request flash object?
    #      Currently, the request is never accessed, and I'm not sure
    #      that it should be.

    def __init__(self, app, request, session):
        self.app = app
        self.request = request
        self.session = session

    def __call__(self, message, key=None):
        self.append(message, key)

    def append(self, message, key=None):
        key = self._key(key)
        if key not in self.session:
            self.session[key] = []
        self.session[key].append(message)
        self.session.save()

    def insert(self, index, message, key=None):
        key = self._key(key)
        if key not in self.session:
            self.session[key] = []
        self.session[key].insert(index, message)
        self.session.save()

    def get(self, key=None):
        key = self._key(key)
        return self.session.get(key, [])

    def pop(self, key=None):
        key = self._key(key)
        if key in self.session:
            messages = self.session.pop(key)
            self.session.save()
            return messages
        return []

    def _key(self, key):
        return '_flash' if not key else '_flash_{}'.format(key)
