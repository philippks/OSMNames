--delete entries with faulty geometries from import
DELETE FROM osm_polygon WHERE ST_IsEmpty(geometry); --&

-- delete linestrings which are also polygons, see #162
DELETE FROM osm_linestring WHERE osm_id = ANY(SELECT osm_id FROM osm_polygon); --&
