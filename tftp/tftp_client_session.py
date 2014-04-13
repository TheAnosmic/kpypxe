
class TFTPClientSession(object):
    def __init__(self, stream, blksize=512):
        """
        stream must support seek method.
        """
        self.block = 1
        self.stream = stream
        self.blksize = blksize

    def get_block(self, block):
        if block != self.block:
            self.stream.seek(block * self.blksize)
        self.block = block + 1
        return self.stream.read(self.blksize)

    def close(self):
        self.stream.close()