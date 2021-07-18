def take_photo():
    # TODO: Take a photo
    with open('temp.png', 'rb') as f:
        data = f.read()
    return data
