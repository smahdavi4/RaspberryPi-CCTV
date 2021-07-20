class CCTV:
    def __init__(self):
        self.schedule = {}

    def take_photo(self):
        # TODO: Take a photo
        with open('temp.png', 'rb') as f:
            data = f.read()
        return data

    def A(self):
        pass


cctv = CCTV()
