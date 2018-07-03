from helpers.functions import geometry_from_wkt
from osmnames.prepare_data.prepare_housenumbers import set_street_attributes_by_nearest_street


def test_street_id_and_name_set_to_nearest_street_with_same_parent(session, tables):
    session.add(
            tables.osm_housenumber(
                    id=1,
                    osm_id=195916994,
                    housenumber=89,
                    parent_id=9999,
                    geometry=geometry_from_wkt("""POLYGON((7.50291155412629
                        46.984637330684,7.50293686747387
                        46.9847717764109,7.50306309893565
                        46.9847606284797,7.50303778558808
                        46.9846263503908,7.50291155412629 46.984637330684))""")
                )
            )

    session.add(
            tables.osm_linestring(
                    id=2,
                    osm_id=25736914,
                    name="Dorfstrasse",
                    parent_id=9999,
                    geometry=geometry_from_wkt("""LINESTRING(7.50604965485542
                        46.9847084930419,7.50411133974654
                        46.9844746379434,7.50263746589252
                        46.9845197325825,7.50072262011252
                        46.9842244381337,7.50006162322825
                        46.9843440478919,7.49898848816497
                        46.9847706867635,7.49873912654556 46.9847848521798)""")
                )
            )

    session.add(
            tables.osm_linestring(
                    id=3,
                    osm_id=26162329,
                    name="Zaelgli",
                    parent_id=9999,
                    geometry=geometry_from_wkt("""LINESTRING(7.50218928552983
                        46.9844405235975,7.50165158644125
                        46.9850208865732,7.50142359867493 46.9861110368999)""")
                )
            )

    session.commit()

    set_street_attributes_by_nearest_street()

    assert session.query(tables.osm_housenumber).get(1).street_id == 25736914
    assert str(session.query(tables.osm_housenumber).get(1).street) == "Dorfstrasse"
