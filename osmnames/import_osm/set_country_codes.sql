DROP FUNCTION IF EXISTS get_country_code_by_geometry(geometry);
CREATE FUNCTION get_country_code_by_geometry(geometry_in GEOMETRY) RETURNS VARCHAR(2) AS $$
BEGIN
  RETURN(
    SELECT lower(country_code)
    FROM country_osm_grid
    WHERE st_intersects(geometry, geometry_in)
    ORDER BY st_area(st_intersection(geometry, geometry_in)) DESC
    LIMIT 1
  );
END;
$$ LANGUAGE plpgsql IMMUTABLE;


DO $$
BEGIN
  -- use imported country code for polygons if present
  UPDATE osm_polygon SET country_code = lower(imported_country_code) WHERE imported_country_code IS NOT NULL;

  -- set missing country codes for every polygon with place_rank <= 4 (countries)
  UPDATE osm_polygon SET country_code = get_country_code_by_geometry(geometry) WHERE country_code = '' IS NOT FALSE
                                                                                     AND place_rank <= 4;

  CREATE INDEX IF NOT EXISTS idx_osm_polygon_country_code ON osm_polygon(country_code);
END
$$ LANGUAGE plpgsql;
