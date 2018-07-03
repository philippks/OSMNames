def test_get_bounding_box(session, tables):
    geometry_switzerland = """POLYGON((5.95591129460078
        46.1323564473647,8.56801356906789 47.8084647540334,10.4893515521603
        46.9377887783714,9.01806007867824 45.8181130300574,5.95591129460078
        46.1323564473647))"""

    bounding_box_switzerland = get_bounding_box(session, geometry_switzerland, "ch", 2)

    assert bounding_box_switzerland == [5.9559113,
                                        45.8181130,
                                        10.4893516,
                                        47.8084648]


def test_bbox_for_countries_with_colonies(session, tables):
    bounding_box_fr = get_bounding_box(session, "POLYGON((0 0,5 0,5 5,0 5,0 0))", "fr", 2)
    assert bounding_box_fr == [-5.225, 41.333, 9.55, 51.2]

    bounding_box_nl = get_bounding_box(session, "POLYGON((0 0,5 0,5 5,0 5,0 0))", "nl", 2)
    assert bounding_box_nl == [3.133, 50.75, 7.217, 53.683]


def test_bbox_for_polygon_crossing_dateline(session, tables):
    geometry_new_zealand = """MULTIPOLYGON(((166.138599289183
        -45.9071981590935,174.899643687336 -40.6134516417377,172.519111353147
        -34.270167130167,178.773685741024 -37.5532522368813,166.138599289183
        -45.9071981590935)))"""

    bbox_new_zealand = get_bounding_box(session, geometry_new_zealand, "nz", 2)

    assert bbox_new_zealand == [166.1385993,
                                -45.9071982,
                                178.7736857,
                                -34.2701671]


def test_bbox_for_shifted_polygon_crossing_dateline(session, tables):
    # SELECT st_astext(st_simplify(geometry, 50000)) FROM osm_polygon WHERE osm_id = -571747;
    geometry_fiji = """MULTIPOLYGON(((176.670074640063
        -17.2112718586013,179.999999917187 -15.5088681805728,179.999999917187
        -19.8005205387898,177.825122941779 -19.3032512248901,176.670074640063
        -17.2112718586013)),((-180 -19.8005205387898,-179.963319534427
        -15.5077817182834,-178.980216672404 -15.9673182186668,-178.030348978473
        -17.8748357007115,-178.579324409031 -21.1288887446798,-180
        -19.8005205387898)))"""

    bbox_fiji = get_bounding_box(session, geometry_fiji, "fj", 4)

    assert bbox_fiji == [176.6700746, -21.1288887, -178.030349, -15.5077817]


def test_bbox_for_falkland_islands(session, tables):
    # SELECT st_astext(st_simplify(geometry, 100000)) FROM osm_polygon WHERE osm_id = -2185374;
    geometry_falkland_island = """MULTIPOLYGON(((-61.772677218624
        -50.9875737757979,-57.8482564064633 -51.1713441530302,-57.3785571837582
        -51.7332428019015,-58.7872839526582 -52.6385132388934,-60.7313259130577
        -52.4530157705123,-61.6360667814072 -51.9242084562749,-61.772677218624
        -50.9875737757979)))"""

    bbox_falkland_island = get_bounding_box(session, geometry_falkland_island, "fk", 2)

    assert bbox_falkland_island == [-61.7726772,
                                    -52.6385132,
                                    -57.3785572,
                                    -50.9875738]


def get_bounding_box(session, geometry, country_code, admin_level):
    query = """SELECT get_bounding_box(
                    ST_SetSRID('{}'::GEOMETRY, 4326),
                    '{}'
                    ,{})""".format(geometry, country_code, admin_level)

    bounding_box = [float(session.execute(query).fetchone()[0][x]) for x in range(4)]
    return bounding_box
