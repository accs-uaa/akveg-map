-- -*- coding: utf-8 -*-
-- ---------------------------------------------------------------------------
-- Query site visits from AKVEG Database
-- Author: Timm Nawrocki, Alaska Center for Conservation Science
-- Last Updated:  2024-07-04
-- Usage: Script should be executed in a PostgreSQL 14+ database.
-- Description: "Query site visits from AKVEG Database" queries all site visit data from the AKVEG Database observed on or after May 5, 2000.
-- ---------------------------------------------------------------------------

-- Compile site visit data
SELECT site_visit.site_visit_code as st_vst
	 , site_visit.project_code as prjct_cd
	 , scope_vascular.scope as scp_vasc
     , scope_bryophyte.scope as scp_bryo
     , scope_lichen.scope as scp_lich
	 , perspective.perspective as perspect
	 , cover_method.cover_method as cvr_mthd
	 , plot_dimensions.plot_dimensions_m as plt_dim_m
	 , site_visit.observe_date as obs_date
     , site.latitude_dd as lat_dd
     , site.longitude_dd as long_dd
FROM site_visit
    LEFT JOIN site ON site_visit.site_code = site.site_code
	LEFT JOIN scope scope_vascular ON site_visit.scope_vascular_id = scope_vascular.scope_id
    LEFT JOIN scope scope_bryophyte ON site_visit.scope_bryophyte_id = scope_bryophyte.scope_id
    LEFT JOIN scope scope_lichen ON site_visit.scope_lichen_id = scope_lichen.scope_id
	LEFT JOIN perspective ON site.perspective_id = perspective.perspective_id
	LEFT JOIN cover_method ON site.cover_method_id = cover_method.cover_method_id
	LEFT JOIN plot_dimensions ON site.plot_dimensions_id = plot_dimensions.plot_dimensions_id
WHERE observe_date >= '2000-05-01';