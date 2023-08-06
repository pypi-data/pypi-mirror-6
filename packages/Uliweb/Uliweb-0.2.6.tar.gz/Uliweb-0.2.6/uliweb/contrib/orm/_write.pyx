def write_row(fw, r, encoding):
    from uliweb.utils.common import str_value
    fw.writerow([str_value(x, encoding=encoding, newline_escape=True) for x in r])
    