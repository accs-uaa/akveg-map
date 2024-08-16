-- -*- coding: utf-8 -*-
-- ---------------------------------------------------------------------------
-- Query vegetation cover from AKVEG Database
-- Author: Timm Nawrocki, Alaska Center for Conservation Science
-- Last Updated:  2024-02-06
-- Usage: Script should be executed in a PostgreSQL 14+ database.
-- Description: "Query vegetation cover from AKVEG Database" queries all vegetation cover data from the AKVEG Database.
-- ---------------------------------------------------------------------------

-- Compile vegetation cover
SELECT vegetation_cover.site_visit_code as st_vst
     , cover_type.cover_type as cvr_type
     , taxon_accepted.taxon_name as name_accepted
     , vegetation_cover.dead_status as dead_status
     , vegetation_cover.cover_percent as cvr_pct
FROM vegetation_cover
	LEFT JOIN site_visit ON vegetation_cover.site_visit_code = site_visit.site_visit_code
    LEFT JOIN cover_type ON vegetation_cover.cover_type_id = cover_type.cover_type_id
    LEFT JOIN taxon_all taxon_adjudicated ON vegetation_cover.code_adjudicated = taxon_adjudicated.taxon_code
    LEFT JOIN taxon_all taxon_accepted ON taxon_adjudicated.taxon_accepted_code = taxon_accepted.taxon_code;