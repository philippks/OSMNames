-----------------------------------
--                               --
--  FUNCTIONS FOR IMPORTING DATA --
--                               --
-----------------------------------

CREATE OR REPLACE FUNCTION rank_place(type TEXT, osmID bigint)
RETURNS int AS $$
BEGIN
	RETURN CASE
		WHEN type IN ('administrative') THEN 2*(SELECT COALESCE(admin_level,15) FROM osm_polygon_tmp o WHERE osm_id = osmID)
		WHEN type IN ('continent', 'sea') THEN 2
		WHEN type IN ('country') THEN 4
		WHEN type IN ('state') THEN 8
		WHEN type IN ('county') THEN 12
		WHEN type IN ('city') THEN 16
		WHEN type IN ('island') THEN 17
		WHEN type IN ('region') THEN 18 -- dropped from previous value of 10
		WHEN type IN ('town') THEN 18
		WHEN type IN ('village','hamlet','municipality','district','unincorporated_area','borough') THEN 19
		WHEN type IN ('suburb','croft','subdivision','isolated_dwelling','farm','locality','islet','mountain_pass') THEN 20
		WHEN type IN ('neighbourhood', 'residential') THEN 22
		WHEN type IN ('houses') THEN 28
		WHEN type IN ('house','building') THEN 30
		WHEN type IN ('quarter') THEN 30
	END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION rank_address(type TEXT)
RETURNS int AS $$
BEGIN
	RETURN CASE
		WHEN type IN ('service','cycleway','path','footway','steps','bridleway','motorway_link','primary_link','trunk_link','secondary_link','tertiary_link') THEN 27
		ELSE 26
	END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


DROP FUNCTION IF EXISTS determine_parent_id(BIGINT, INT, GEOMETRY);
CREATE FUNCTION determine_parent_id(id_value BIGINT, rank_search_value INT, geometry_value GEOMETRY) RETURNS BIGINT AS $$
DECLARE
  parent_id BIGINT;
BEGIN
  SELECT id FROM osm_polygon WHERE ST_Contains(geometry, geometry_value)
                                   AND NOT id=id_value
                                   AND NOT ST_Equals(geometry, geometry_value)
                                   AND rank_search <= rank_search_value
                             ORDER BY rank_search DESC, admin_level DESC
                             LIMIT 1
                             INTO parent_id;

RETURN parent_id;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS findRoadsWithinGeometry(BIGINT, geometry);
CREATE FUNCTION findRoadsWithinGeometry(id_value BIGINT, geometry_value GEOMETRY) RETURNS VOID AS $$
BEGIN
  UPDATE osm_linestring SET parent_id = id_value WHERE parent_id IS NULL AND ST_Contains(geometry_value, geometry);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION determineRoadHierarchyForEachCountry() RETURNS void AS $$
DECLARE
  retVal BIGINT;
BEGIN
  FOR current_rank  IN REVERSE 22..4 LOOP
    PERFORM findRoadsWithinGeometry(id, geometry) FROM osm_polygon WHERE rank_search = current_rank;
  END LOOP;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS get_country_code_from_geometry(GEOMETRY);
CREATE FUNCTION get_country_code_from_geometry(geometry GEOMETRY)
RETURNS VARCHAR(2) AS $$
DECLARE
  geometry_centre GEOMETRY;
  country RECORD;
BEGIN
  geometry_centre := ST_PointOnSurface(geometry);

  FOR country IN SELECT country_code FROM country_osm_grid WHERE ST_COVERS(country_osm_grid.geometry, geometry_centre)
                                                           ORDER BY area ASC LIMIT 1
  LOOP
    RETURN country.country_code;
  END LOOP;

  FOR country IN SELECT country_code FROM country_osm_grid WHERE ST_DWITHIN(country_osm_grid.geometry, geometry_centre, 0.5)
                                                           ORDER BY ST_DISTANCE(country_osm_grid.geometry, geometry_centre) ASC,
                                                           area ASC LIMIT 1
  LOOP
    RETURN country.country_code;
  END LOOP;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


DROP FUNCTION IF EXISTS get_rank_search(VARCHAR, BIGINT);
CREATE FUNCTION get_rank_search(type VARCHAR, osm_id BIGINT)
RETURNS INTEGER AS $$
BEGIN
  IF (osm_id IS NULL) THEN
    RETURN rank_address(type);
  ELSE
    RETURN rank_place(type, osm_id);
  END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


DROP FUNCTION IF EXISTS get_country_code(INTEGER, GEOMETRY, VARCHAR);
CREATE FUNCTION get_country_code(rank_search INTEGER, geometry GEOMETRY, imported_country_code VARCHAR)
RETURNS VARCHAR(2) AS $$
BEGIN
  IF rank_search = 4 AND imported_country_code IS NOT NULL THEN
    -- for countries, believe the mapped country code,
    -- so that we remain in the right partition if the boundaries
    -- suddenly expand.
    RETURN imported_country_code;
  END IF;

  IF rank_search >= 4 THEN
    RETURN get_country_code_from_geometry(geometry);
  END IF;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;



DROP FUNCTION IF EXISTS get_country_code_from_imported_data(GEOMETRY);
CREATE FUNCTION get_country_code_from_imported_data(geom GEOMETRY)
RETURNS VARCHAR(2) AS $$
DECLARE
  result VARCHAR(2);
BEGIN
  SELECT country_code FROM osm_polygon WHERE ST_Within(ST_PointOnSurface(geom), geometry)
                                             AND rank_search = 4
                                             AND NOT country_code IS NULL
                                       LIMIT 1
                                       INTO result;
  return result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
