DROP MATERIALIZED VIEW IF EXISTS mv_polygons;
CREATE MATERIALIZED VIEW mv_polygons AS
SELECT
  id,
  relationName AS name,
  alternative_names,
  CASE WHEN osm_id > 0 THEN 'way' ELSE 'relation' END AS osm_type,
  abs(osm_id)::VARCHAR as osm_id,
  determine_class(relation_type) AS class,
  relation_type,
  ST_X(ST_PointOnSurface(ST_Buffer(ST_Transform(geometry, 4326), 0.0))) AS lon,
  ST_Y(ST_PointOnSurface(ST_Buffer(ST_Transform(geometry, 4326), 0.0))) AS lat,
  place_rank AS place_rank,
  get_importance(place_rank, wikipedia, relevant_country_code) AS importance,
  ''::TEXT AS street,
  COALESCE(parentInfo.city, '') AS city,
  COALESCE(parentInfo.county, '') AS county,
  COALESCE(parentInfo.state, '') AS state,
  COALESCE(country_name(relevant_country_code), '') AS country,
  COALESCE(relevant_country_code, '') AS country_code,
  parentInfo.displayName  AS display_name,
  ST_XMIN(ST_Transform(geometry, 4326)) AS west,
  ST_YMIN(ST_Transform(geometry, 4326)) AS south,
  ST_XMAX(ST_Transform(geometry, 4326)) AS east,
  ST_YMAX(ST_Transform(geometry, 4326)) AS north,
  wikidata AS wikidata,
  wikipedia AS wikipedia
FROM
  osm_polygon,
  getLanguageName(name, name_fr, name_en, name_de, name_es, name_ru, name_zh) AS languageName,
  get_parent_info(languageName, parent_id, place_rank) AS parentInfo,
  getTypeForRelations(linked_osm_id, type, place_rank) AS relation_type,
  COALESCE(NULLIF(getNameForRelations(linked_osm_id, relation_type), ''), languageName) AS relationName,
  getAlternativesNames(name, name_fr, name_en, name_de, name_es, name_ru, name_zh, relationName, ',') AS alternative_names,
  COALESCE(NULLIF(osm_polygon.country_code, ''), parentInfo.country_code) AS relevant_country_code
;
