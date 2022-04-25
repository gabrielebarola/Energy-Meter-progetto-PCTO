import btree


class Logger:
    def __init__(self, path):
        try:
            self.f = open(path, "r+b")
        except OSError:
            self.f = open(path, "w+b")

        self.db = btree.open(self.f)

    def log(self, time: int, data:list):
        #convert time and data to strings
        time, data = str(time), "-".join([str(d) for d in data])

        #insert in the db as bytes
        self.db[time.encode()] = data.encode()
        self.db.flush()

    def decode_data(self, encoded_data: bytes) -> list:
        return encoded_data.decode().split('-')

    def close(self):
        self.db.close()
        self.f.close()
