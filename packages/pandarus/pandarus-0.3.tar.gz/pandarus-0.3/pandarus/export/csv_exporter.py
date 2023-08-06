try:
    from unicodecsv import writer
except ImportError:
    from ._unicodecsv import writer


def csv_exporter(data, filepath, **kwargs):
    w = writer(open(filepath, "w"), encoding='utf-8')
    for key, value in data.iteritems():
        w.writerow((key[0], key[1], value))
    return filepath
