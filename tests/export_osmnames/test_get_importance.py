def test_returns_place_rank_importance_if_no_wikipedia_article_exists(session, tables):
    importance = get_importance(session, 12, "de:Hombrechtikon", "ch", [])

    assert importance == 0.45


def test_returns_place_rank_calculates_importance_if_no_wikipedia_article_defined(session, tables):
    importance = get_importance(session, 12, "", "ch", [])

    assert importance == 0.45


def test_returns_wikipedia_importance_if_it_is_highest(session, tables):
    session.add(tables.wikipedia_article(language="de", title="POI", importance=10))
    session.add(
            tables.osm_point(
                id=1,
                osm_id=10,
                place_rank=12
            )
        )
    session.commit()

    importance = get_importance(session, 12, "de:POI", "ch", [10])

    assert importance == 10


def test_returns_linked_osm_ids_importance_if_it_is_highest(session, tables):
    session.add(tables.wikipedia_article(language="de", title="POI", importance=0.3))
    session.add(
            tables.osm_point(
                id=1,
                osm_id=10,
                place_rank=12
            )
        )
    session.commit()

    importance = get_importance(session, 6, "de:POI", "ch", [10])

    assert importance == 0.45


def get_importance(session, place_rank, wikipedia, country_code, linked_osm_ids):
    query = "SELECT get_importance({},'{}','{}', ARRAY[{}]::bigint[])".format(place_rank,
                                                                              wikipedia,
                                                                              country_code,
                                                                              ','.join(map(str, linked_osm_ids)))
    return session.execute(query).fetchone()[0]
