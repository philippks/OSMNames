from geoalchemy2.elements import WKTElement


def geometry_from_wkt(wkt):
    return WKTElement(wkt, srid=4326)
