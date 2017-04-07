DROP TABLE IF EXISTS osm_polygon CASCADE;
CREATE TABLE osm_polygon AS
(SELECT
    100000000 + id AS id,
    osm_id,
    type,
    name,
    name_fr,
    name_en,
    name_de,
    name_es,
    name_ru,
    name_zh,
    wikipedia,
    wikidata,
    admin_level,
    geometry,
    rank_search,
    country_code,
    NULL::bigint AS parent_id,
    NULL::bigint AS linked_osm_id
FROM
    osm_polygon_tmp p,
    get_rank_search(type, osm_id) AS rank_search,
    get_country_code(rank_search, geometry, imported_country_code) AS country_code
);
ALTER TABLE osm_polygon ADD PRIMARY KEY (id);


DROP TABLE IF EXISTS osm_point CASCADE;
CREATE TABLE osm_point AS
(SELECT
    200000000 + id AS id,
    osm_id,
    type,
    name,
    name_fr,
    name_en,
    name_de,
    name_es,
    name_ru,
    name_zh,
    wikipedia,
    wikidata,
    admin_level,
    geometry,
    rank_search,
    country_code,
    NULL::bigint AS parent_id,
    FALSE::boolean AS linked
FROM
    osm_point_tmp,
    get_rank_search(type, osm_id) AS rank_search,
    get_country_code(rank_search, geometry, NULL) AS country_code
);
ALTER TABLE osm_point ADD PRIMARY KEY (id);


DROP TABLE IF EXISTS osm_linestring CASCADE;
CREATE TABLE osm_linestring AS
(SELECT
    300000000 + id AS id,
    osm_id,
    type,
    name,
    name_fr,
    name_en,
    name_de,
    name_es,
    name_ru,
    name_zh,
    wikipedia,
    wikidata,
    admin_level,
    geometry,
    rank_search,
    country_code,
    NULL::bigint AS parent_id,
    FALSE::boolean AS merged
FROM
    osm_linestring_tmp,
    get_rank_search(type, NULL) AS rank_search,
    get_country_code(rank_search, geometry, NULL) AS country_code
);
ALTER TABLE osm_linestring ADD PRIMARY KEY (id);


--create indexes
CREATE INDEX IF NOT EXISTS idx_osm_polgyon_geom ON osm_polygon USING gist (geometry);
CREATE INDEX IF NOT EXISTS idx_osm_point_geom ON osm_point USING gist (geometry);
CREATE INDEX IF NOT EXISTS idx_osm_linestring_geom ON osm_linestring USING gist (geometry);
CREATE INDEX IF NOT EXISTS idx_osm_polygon_country_code_rank ON osm_polygon (country_code, rank_search);
CREATE INDEX IF NOT EXISTS idx_osm_polygon_id ON osm_polygon (id);
CREATE INDEX IF NOT EXISTS idx_osm_point_osm_id ON osm_point (osm_id);
CREATE INDEX IF NOT EXISTS idx_osm_linestring_id ON osm_linestring (id);

--determine missed partition and country codes from import dataset
UPDATE osm_polygon SET country_code = get_country_code_from_imported_data(geometry)
WHERE country_code IS NULL;

UPDATE osm_point SET country_code = get_country_code_from_imported_data(geometry)
WHERE country_code IS NULL;

UPDATE osm_linestring SET country_code = get_country_code_from_imported_data(geometry)
WHERE country_code IS NULL;
