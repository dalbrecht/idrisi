

class Model:

    def __init__(self, metadata_dict, parent_model=None, persistence=None):
        self._children = list()
        self._parent_model = parent_model
        self.process_metadata(metadata_dict)
        self.persistence=persistence
        return

    def process_metadata(self, metadata_dict):
        return

    def scrape(self):
        return

    def get_children(self):
        return self._children

    def save_children(self):
        for child in self._children:
            child.save()

    def get_parent(self):
        return self._parent_model

    def get_type(self):
        return self._type

    def save(self, recurse=False):
        return