import math


def svg_piechart(pct, x, y, radius):

    ANGLE = 360 * float(pct)
    START_ANGLE = -90
    END_ANGLE = START_ANGLE + ANGLE

    x2 = x + int(math.cos(END_ANGLE * math.pi / 180) * radius)
    y2 = y + int(math.sin(END_ANGLE * math.pi / 180) * radius)

    rot = 1 if pct > 0.5 else 0

    d = "M50 15 A{0}, {0} 0 {1}, 1 {2}, {3} L50 50 Z".format(radius, rot, x2, y2)

    svg = """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
            <circle cx="50" cy="50" r="45" fill="#f5f5ed" stroke-width="1" stroke="#999999" />
            <path fill="#65c500" d="%s" />
        </svg>""" % d

    return svg.strip()


def svg_housinghistory(years):

    bpad = 50       # bottom padding
    tpad = 23       # top padding
    gheight = 100   # height of the graph area

    wpx = 80        # column width in pixels

    maxval = max(x for x in years.values() if x)
    minval = min(x for x in years.values() if x)
    diffval = maxval - minval

    print minval, maxval

    path = ["M0 173"]

    (x, y) = (0, 0)

    for year in sorted(years.keys()):

        units = years[year]

        if units is None:
            path.append("L%i 173" % x)

        else:

            if diffval:

                y = ((units - minval) / diffval) * gheight

            else:

                y = 100

            path.append("L%i %i" % (x, tpad + (100 - y)))

        x += wpx

    path.append("L320 173")
    path.append("Z")

    svg = """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
            <line x1="0" y1="23" x2="320" y2="23" stroke="#d9d7d2" stroke-width="1" stroke-dasharray="2,2" />
            <line x1="0" y1="73" x2="320" y2="73" stroke="#d9d7d2" stroke-width="1" stroke-dasharray="2,2" />
            <line x1="0" y1="123" x2="320" y2="123" stroke="#d9d7d2" stroke-width="1" stroke-dasharray="2,2" />
            <path fill="#836b98" d="%s" />
            <text x="5" y="37" font-family="Verdana" font-size="10" fill="#b9b7b2">%s</text>
            <text x="5" y="137" font-family="Verdana" font-size="10" fill="#b9b7b2">%s</text>
        </svg>""" % (" ".join(path), maxval, minval if minval < maxval else "")

    svg = svg.strip().replace("\n", "")

    return svg
