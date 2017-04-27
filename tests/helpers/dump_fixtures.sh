#!/bin/bash

# helper command to create sql dumps for tests
pg_dump --no-owner --schema-only --schema="public" --clean --if-exists -t 'osm_*' -t country_osm_grid -t country_name osm > $1
