import gzip
import io
import StringIO


def gzip_compress(content):
    stringio = StringIO.StringIO()
    gzip_file = gzip.GzipFile(None, 'wb', 9, stringio)
    gzip_file.write(content)
    gzip_file.close()
    return stringio.getvalue()


def gzip_decompress(content):
    try:
        binary_content = io.BytesIO(content)
        gzip_file = gzip.GzipFile(fileobj=binary_content, mode="rb")
        return gzip_file.read()
    except IOError:
        return None
