import tempfile


def tmp():
    tmpdir = tempfile.mkdtemp()
    return tmpdir


if __name__ == '__main__':
    tmp()
