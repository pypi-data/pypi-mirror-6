import bz2
import codecs
import json


def json_exporter(data, filepath, compressed=True):
    reformatted = [(k[0], k[1], v) for k, v in data.iteritems()]
    if compressed:
        filepath += ".bz2"
        with bz2.BZ2File(filepath, "w") as f:
            f.write(json.dumps(reformatted, ensure_ascii=False).encode('utf-8'))
    else:
        with codecs.open(filepath, "w", encoding="utf-8") as f:
            json.dump(reformatted, f, ensure_ascii=False)
    return filepath
