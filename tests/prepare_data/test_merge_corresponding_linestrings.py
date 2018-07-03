from helpers.functions import geometry_from_wkt
from osmnames.prepare_data.prepare_data import merge_corresponding_linestrings


TOUCHING_LINESTRING_LHS = geometry_from_wkt("""LINESTRING(8.48772097163589
        47.2647943976317,8.48773622669969 47.2649455233459,8.4877325386623
        47.2650472796504)""")

TOUCHING_LINESTRING_RHS = geometry_from_wkt("""LINESTRING(8.4877325386623
        47.2650472796504,8.48765224002989 47.2652291669493,8.48755727306693
        47.2655106312578,8.48752374545424 47.2656923509186)""")


def test_touching_linestrings_with_same_name_and_parent_id_get_merged(session, tables):
    session.add(
            tables.osm_linestring(
                id=1,
                osm_id=1111,
                name="Rigiweg",
                parent_id=1337,
                geometry=TOUCHING_LINESTRING_LHS)
            )

    session.add(
            tables.osm_linestring(
                id=2,
                osm_id=2222,
                name="Rigiweg",
                parent_id=1337,
                geometry=TOUCHING_LINESTRING_RHS)
            )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_merged_linestring).get(1).member_ids == [1, 2]
    assert session.query(tables.osm_linestring).get(1).merged_into == 1111
    assert session.query(tables.osm_linestring).get(2).merged_into == 1111


def test_multiple_touching_linestrings_with_same_name_and_parent_id_get_merged(session, tables):
    # following geometries are simplified from the osm linestring with the osm_id 35901448
    session.add(
            tables.osm_linestring(
                id=1,
                osm_id=1111,
                name="Dorfstrasse",
                parent_id=1337,
                geometry=geometry_from_wkt("""LINESTRING(8.49143314891339
                    47.266034081111,8.49021098361167
                    47.2664179722763,8.4883740895312
                    47.2664876258917,8.48667625122436
                    47.2673113993356,8.48528493911658 47.267721693496)""")
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                osm_id=2222,
                name="Dorfstrasse",
                parent_id=1337,
                geometry=geometry_from_wkt("""LINESTRING(8.48378684156239
                    47.2669804817983,8.48203988530295 47.2675886726926)""")
            )
        )

    session.add(
            tables.osm_linestring(
                id=3,
                osm_id=3333,
                name="Dorfstrasse",
                parent_id=1337,
                geometry=geometry_from_wkt("""LINESTRING(8.48378684156239
                    47.2669804817983,8.48528493911658 47.267721693496)""")
            )
        )

    session.add(
            tables.osm_linestring(
                id=4,
                osm_id=4444,
                name="Dorfstrasse",
                parent_id=1337,
                geometry=geometry_from_wkt("""LINESTRING(8.49165116221493
                    47.2659501782602,8.49163766735083
                    47.266055035869,8.49143314891339
                    47.266034081111,8.49146935873511
                    47.2659238590843,8.49165116221493 47.2659501782602)""")
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_merged_linestring).get(1).member_ids == [1, 2, 3, 4]
    assert session.query(tables.osm_linestring).get(1).merged_into == 1111
    assert session.query(tables.osm_linestring).get(2).merged_into == 1111
    assert session.query(tables.osm_linestring).get(3).merged_into == 1111
    assert session.query(tables.osm_linestring).get(4).merged_into == 1111


def test_almost_touching_linestrings_with_same_name_and_parent_id_get_merged(session, tables):
    # the following geometries do not touch directly but has to be merged
    session.add(
            tables.osm_linestring(
                id=1,
                name="Oberseestrasse",
                parent_id=1337,
                osm_id=24055427,
                geometry=geometry_from_wkt("""LINESTRING(8.81655107975993
                    47.2240767883953,8.81666909695662
                    47.2240164386925,8.81688392513493
                    47.2240535705235,8.8172902798008 47.2240774589477)""")
            )
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Oberseestrasse",
                parent_id=1337,
                osm_id=308577271,
                geometry=geometry_from_wkt("""LINESTRING(8.81748876326793
                    47.224078464776,8.81853306458433 47.2239685780254)""")
            )
        )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_merged_linestring).get(1).member_ids == [1, 2]
    assert session.query(tables.osm_linestring).get(1).merged_into == 24055427
    assert session.query(tables.osm_linestring).get(2).merged_into == 24055427


def test_touching_linestrings_with_same_name_but_different_parent_id_dont_get_merged(session, tables):
    session.add(
            tables.osm_linestring(
                id=1,
                name="Rigiweg",
                parent_id=1337,
                geometry=TOUCHING_LINESTRING_LHS)
        )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Rigiweg",
                parent_id=9999,
                geometry=TOUCHING_LINESTRING_RHS)
        )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_linestring).get(1).merged_into is None
    assert session.query(tables.osm_linestring).get(2).merged_into is None


def test_touching_linestrings_with_same_parent_id_but_different_name_dont_get_merged(session, tables):
    session.add(
            tables.osm_linestring(
                id=1,
                name="Rigiweg",
                parent_id=1337,
                geometry=TOUCHING_LINESTRING_LHS)
            )

    session.add(
            tables.osm_linestring(
                id=2,
                name="Zueristrasse",
                parent_id=1337,
                geometry=TOUCHING_LINESTRING_RHS)
            )

    session.commit()

    merge_corresponding_linestrings()

    assert session.query(tables.osm_linestring).get(1).merged_into is None
    assert session.query(tables.osm_linestring).get(2).merged_into is None
