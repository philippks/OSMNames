import pytest
import os

from geoalchemy2.elements import WKTElement
from osmnames.database.functions import exec_sql_from_file
from osmnames.import_osm.import_osm import merge_corresponding_linestrings


@pytest.fixture(scope="function")
def schema(engine):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    exec_sql_from_file('fixtures/test_prepare_imported_data.sql.dump', cwd=current_directory)


def test_touching_linestrings_with_same_name_and_parent_id_get_merged(session, schema, tables):
    session.add(
            tables.osm_linestring(
                id=1,
                name="Rigiweg",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944848.776557897 5985402.86960293,
                    944850.474743831 5985427.66032806,944850.064193386
                    5985444.35251452)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Rigiweg",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944850.064193386 5985444.35251452,
                    944841.125390515 5985474.18953402,944830.553716556 5985520.36149253,
                    944826.821439784 5985550.17127335)""", srid=3857)
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_merged_multi_linestring).get(1).member_ids, [1, 2]
    assert session.query(tables.osm_linestring).get(1).merged_into, 1
    assert session.query(tables.osm_linestring).get(2).merged_into, 1


def test_multiple_touching_linestrings_with_same_name_and_parent_id_get_merged(session, schema, tables):
    # following geometries are simplified from the osm linestring with the id 35901448
    session.add(
            tables.osm_linestring(
                id=1,
                name="Dorfstrasse",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(945262.014242162 5985606.22988835,
                    945125.963423109 5985669.20516832,944921.48130943 5985680.63151807,
                    944732.478813664 5985815.76883825,
                    944577.598658291 5985883.07702847)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Dorfstrasse",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944410.8312014 5985761.48265348,
                    944216.360920161 5985861.25509228)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=3,
                name="Dorfstrasse",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944410.8312014 5985761.48265348,
                    944577.598658291 5985883.07702847)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=4,
                name="Dorfstrasse",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(945286.283371876 5985592.46613797,
                    945284.781130476 5985609.66739185,945262.014242162 5985606.22988835,
                    945266.045101078 5985588.14864235,
                    945286.283371876 5985592.46613797)""", srid=3857)
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_merged_multi_linestring).get(1).member_ids, [1, 2, 3, 4]
    assert session.query(tables.osm_linestring).get(1).merged_into, 1
    assert session.query(tables.osm_linestring).get(2).merged_into, 1
    assert session.query(tables.osm_linestring).get(3).merged_into, 1
    assert session.query(tables.osm_linestring).get(4).merged_into, 1


def test_almost_touching_linestrings_with_same_name_and_parent_id_get_merged(session, schema, tables):
    # the following geometries do not touch directly but has to be merged
    session.add(
            tables.osm_linestring(
                id=1,
                name="Oberseestrasse",
                parent_id=1337,
                country_code="ch",
                osm_id=24055427,
                geometry=WKTElement("""LINESTRING(981453.976751762
                    5978726.11248254,981467.114366002 5978716.22031828,981491.02892942
                    5978722.30674579,981536.264123906 5978726.22239555)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Oberseestrasse",
                parent_id=1337,
                country_code="ch",
                osm_id=308577271,
                geometry=WKTElement("""LINESTRING(981558.359202398
                    5978726.38726504,981674.610293174 5978708.37529047)""", srid=3857)
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_merged_multi_linestring).get(1).member_ids, [1, 2]
    assert session.query(tables.osm_linestring).get(1).merged_into, 1
    assert session.query(tables.osm_linestring).get(2).merged_into, 1


def test_touching_linestrings_with_same_name_but_different_parent_id_dont_get_merged(session, schema, tables):
    session.add(
            tables.osm_linestring(
                id=1,
                name="Rigiweg",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944848.776557897 5985402.86960293,
                    944850.474743831 5985427.66032806,944850.064193386
                    5985444.35251452)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Rigiweg",
                parent_id=9999,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944850.064193386 5985444.35251452,
                    944841.125390515 5985474.18953402,944830.553716556 5985520.36149253,
                    944826.821439784 5985550.17127335)""", srid=3857)
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert str(session.query(tables.osm_linestring).get(1).merged_into), False
    assert str(session.query(tables.osm_linestring).get(2).merged_into), False


def test_touching_linestrings_with_same_parent_id_but_different_name_dont_get_merged(session, schema, tables):
    session.add(
            tables.osm_linestring(
                id=1,
                name="Rigiweg",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944848.776557897 5985402.86960293,
                    944850.474743831 5985427.66032806,944850.064193386
                    5985444.35251452)""", srid=3857)
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Zueristrasse",
                parent_id=1337,
                country_code="ch",
                geometry=WKTElement("""LINESTRING(944850.064193386 5985444.35251452,
                    944841.125390515 5985474.18953402,944830.553716556 5985520.36149253,
                    944826.821439784 5985550.17127335)""", srid=3857)
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert str(session.query(tables.osm_linestring).get(1).merged_into), False
    assert str(session.query(tables.osm_linestring).get(2).merged_into), False
