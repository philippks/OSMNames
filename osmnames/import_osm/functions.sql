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


CREATE OR REPLACE FUNCTION determine_parent_id(id_value BIGINT, partition_value INT, rank_search_value INT, geometry_value GEOMETRY) RETURNS BIGINT AS $$
DECLARE
  parent_id BIGINT;
BEGIN
  SELECT id FROM osm_polygon WHERE partition=partition_value
                                   AND ST_Contains(geometry, geometry_value)
                                   AND NOT id=id_value
                                   AND NOT ST_Equals(geometry, geometry_value)
                                   AND rank_search <= rank_search_value
                             ORDER BY rank_search DESC
                             LIMIT 1
                             INTO parent_id;

RETURN parent_id;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS findRoadsWithinGeometry(BIGINT,INT,geometry);
CREATE OR REPLACE FUNCTION findRoadsWithinGeometry(id_value BIGINT,partition_value INT, geometry_value GEOMETRY) RETURNS VOID AS $$
BEGIN
	UPDATE osm_linestring SET parent_id = id_value WHERE parent_id IS NULL AND ST_Contains(geometry_value,geometry);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION determineRoadHierarchyForEachCountry() RETURNS void AS $$
DECLARE
  retVal BIGINT;
BEGIN
  FOR current_partition  IN 1..255 LOOP
    FOR current_rank  IN REVERSE 22..4 LOOP
       PERFORM findRoadsWithinGeometry(id, current_partition, geometry) FROM osm_polygon WHERE partition = current_partition AND rank_search = current_rank;
    END LOOP;
  END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_partition(geometry GEOMETRY) RETURNS INTEGER
  AS $$
DECLARE
  geometry_centre GEOMETRY;
  country RECORD;
BEGIN
  geometry_centre := ST_PointOnSurface(geometry);

  FOR country IN SELECT country_code FROM country_osm_grid WHERE ST_COVERS(country_osm_grid.geometry, geometry_centre)
                                                           ORDER BY area ASC LIMIT 1
  LOOP
    RETURN get_partition_by_country_code(country.country_code);
  END LOOP;

  FOR country IN SELECT country_code FROM country_osm_grid WHERE ST_DWITHIN(country_osm_grid.geometry, geometry_centre, 0.5)
                                                           ORDER BY ST_DISTANCE(country_oms_grid.geometry, geometry_centre) ASC,
                                                           area ASC LIMIT 1
  LOOP
    RETURN get_partition_by_country_code(country.country_code);
  END LOOP;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION get_rank_search(type VARCHAR, osm_id bigint)
RETURNS INTEGER AS $$
BEGIN
  IF (osm_id IS NULL) THEN
    RETURN rank_address(type);
  ELSE
    RETURN rank_place(type, osm_id);
  END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION get_rank_search_and_partition(type VARCHAR, geometry GEOMETRY, osm_id BIGINT, country_code VARCHAR)
RETURNS rankPartitionCode AS $$
DECLARE
  place_centroid GEOMETRY;
  result rankPartitionCode;
BEGIN
  result.rank_search = get_rank_search(type, osm_id);

  IF result.rank_search = 4 THEN
    -- for countries, believe the mapped country code,
    -- so that we remain in the right partition if the boundaries
    -- suddenly expand.
    result.partition := get_partition_by_country_code(country_code);

    IF result.partition = 0 THEN
      result.partition := get_partition(ST_PointOnSurface(geometry));
    END IF;
  ELSIF result.rank_search > 4 THEN
    result.partition := get_partition(ST_PointOnSurface(geometry));
  END IF;

  RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE OR REPLACE FUNCTION get_partition_by_country_code(country_code_in VARCHAR) RETURNS INTEGER AS $$
  SELECT partition FROM country_name WHERE lower(country_code) = lower(country_code_in);
$$ LANGUAGE 'sql' IMMUTABLE;


CREATE OR REPLACE FUNCTION determinePartitionFromImportedData(geom geometry)
RETURNS INTEGER AS $$
DECLARE
  result INTEGER;
BEGIN
  SELECT partition FROM osm_polygon WHERE ST_Within(ST_PointOnSurface(geom), geometry)
                                          AND rank_search = 4
                                          AND NOT partition = 0
                                    INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
