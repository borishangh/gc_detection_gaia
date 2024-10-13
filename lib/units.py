def ra_to_deg(ra):
    h = int(ra[: ra.index("h")])
    m = int(ra[ra.index("h") + 1 : ra.index("m")])
    s = float(ra[ra.index("m") + 1 : ra.index("s")])

    degrees = 15 * (h + m / 60 + s / 3600)
    return degrees

def ra_to_hms(ra):
    max = ra / 15.0
    
    h = int(max)
    m = int((max - h) * 60)
    s = round(((max - h) * 60 - m) * 60, 2)
    
    return f"{h:02d}h{m:02d}m{s:05.2f}s"