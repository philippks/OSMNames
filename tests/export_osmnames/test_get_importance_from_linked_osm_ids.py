def test_returns_null_if_no_linked_osm_ids(session, tables):
    importance = get_importance_from_linked_osm_ids(session, [])

    assert importance is None


def test_returns_importance_of_linked_osm_id(session, tables):
    session.add(
            tables.osm_point(
                id=1,
                osm_id=10,
                place_rank=12
            )
        )
    session.commit()

    importance = get_importance_from_linked_osm_ids(session, [10])

    # importance is 0.45 because place_rank is 12
    assert importance == 0.45


def test_returns_max_importance_of_multiple_linked_osm_ids(session, tables):
    session.add(
            tables.osm_point(
                id=1,
                osm_id=1111,
                place_rank=12,
            )
        )
    session.add(
            tables.osm_point(
                id=2,
                osm_id=2222,
                wikipedia='de:POI',
                parent_id=3
            )
        )
    session.add(
            tables.osm_polygon(
                id=3,
                name="a village",
                country_code="ch"
            )
        )
    session.add(tables.wikipedia_article(language="de", title="POI", importance=10))
    session.commit()

    importance = get_importance_from_linked_osm_ids(session, [1111, 2222])

    assert importance == 10


def get_importance_from_linked_osm_ids(session, linked_osm_ids):
    query = "SELECT get_importance_from_linked_osm_ids(ARRAY[{}]::bigint[])".format(','.join(map(str, linked_osm_ids)))
    return session.execute(query).fetchone()[0]
