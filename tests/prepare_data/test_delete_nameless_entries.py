from geoalchemy2.elements import WKTElement
from osmnames.prepare_data.prepare_data import delete_nameless_entries

POLYGON_GEOMETRY = WKTElement('POLYGON((1 2, 3 4, 5 6, 1 2))', srid=3857)


def test_osm_polygon_with_blank_names_get_deleted(session, tables):
    session.add(tables.osm_polygon(name="gugus"))
    session.add(tables.osm_polygon(name=""))
    session.commit()

    delete_nameless_entries()

    assert session.query(tables.osm_polygon).count() == 1


def test_osm_polygon_with_null_names_get_deleted(session, tables):
    session.add(tables.osm_polygon(name="gugus"))
    session.add(tables.osm_polygon())
    session.commit()

    delete_nameless_entries()

    assert session.query(tables.osm_polygon).count() == 1


def test_osm_point_with_blank_names_get_deleted(session, tables):
    session.add(tables.osm_point(name="gugus"))
    session.add(tables.osm_point(name=""))
    session.commit()

    delete_nameless_entries()

    assert session.query(tables.osm_point).count() == 1


def test_osm_linestring_with_blank_names_get_deleted(session, tables):
    session.add(tables.osm_linestring(name="gugus"))
    session.add(tables.osm_linestring(name=""))
    session.commit()

    delete_nameless_entries()

    assert session.query(tables.osm_linestring).count() == 1
