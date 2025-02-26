def ra_decimal(ra):
    h, m, s = [int(i) for i in ra.split(":")]
    return 15 * (h + m / 60 + s / 3600)


def dec_decimal(dec):
    d, m, s = [int(i) for i in dec.split(":")]
    return d + m / 60 + s / 3600
