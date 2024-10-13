def ra_to_deg(ra):
    h = int(ra[: ra.index("h")])
    m = int(ra[ra.index("h") + 1 : ra.index("m")])
    s = int(ra[ra.index("m") + 1 : ra.index("s")])

    degrees = 15 * (h + m / 60 + s / 3600)
    return degrees
