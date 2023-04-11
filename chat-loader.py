import pickle


class Loader:
    def __init__(self):
        self.data = []

    def load(self):
        with open("messages.list", "rb") as file:
            self.data = pickle.load(file)

    def get_data(self):
        return self.data


loader = Loader()
loader.load()
for message in loader.get_data():
    print(message)
