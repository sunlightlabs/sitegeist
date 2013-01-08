from decimal import Decimal
import locale

TWOPLACES = Decimal("0.01")
locale.setlocale(locale.LC_ALL, '')


def dec2curr(d, whole=False):
    if d is None:
        return ""
    curr = locale.currency(d, grouping=True)
    if whole:
        curr = curr.rsplit(".", 1)[0]
    return curr


def dec2num(d, whole=False):
    if d is None:
        return ""
    format = "%i" if whole else "%0.2f"
    return locale.format(format, d, grouping=True)


def dec2pct(d, raw=False, whole=False):
    if d is None:
        return ""
    if not raw:
        d = d * 100
    return "%i%%" % d if whole else "%0.1f%%" % d
