DO $$
DECLARE
  touching_ids BIGINT[];
BEGIN
  FOR touching_ids IN
    (
      SELECT
        array_agg(DISTINCT lhs.id)
      FROM
        osm_linestring AS lhs,
        osm_linestring AS rhs
      WHERE
        ST_Touches(lhs.geometry, rhs.geometry)
        AND lhs.country_code = rhs.country_code
        AND lhs.parent_id = rhs.parent_id
        AND lhs.parent_id IS NOT NULL
        AND lhs.name = rhs.name
        AND lhs.id != rhs.id
      GROUP BY
        lhs.parent_id,
        lhs.name
    )
  LOOP
    UPDATE osm_linestring SET merged_into = touching_ids[1] WHERE id = ANY(touching_ids);
  END LOOP;
END;
$$ LANGUAGE plpgsql;

DROP VIEW IF EXISTS osm_aggregated_merged_linestrings_view;
CREATE VIEW osm_aggregated_merged_linestrings_view AS
  SELECT
    min(id) AS id,
    max(osm_id::VARCHAR) AS osm_id,
    min(parent_id) AS parent_id,
    max(type) AS type,
    ST_UNION(array_agg(geometry)) AS geometry,
    max(place_rank) AS place_rank,
    max(name) AS name,
    max(name_fr) AS name_fr,
    max(name_en) AS name_en,
    max(name_de) AS name_de,
    max(name_es) AS name_es,
    max(name_ru) AS name_ru,
    max(name_zh) AS name_zh,
    min(country_code) AS country_code,
    max(wikidata) AS wikidata,
    max(wikipedia) AS wikipedia
FROM osm_linestring
WHERE merged_into IS NOT NULL
GROUP BY merged_into;
