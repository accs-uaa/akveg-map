-- -*- coding: utf-8 -*-
-- ---------------------------------------------------------------------------
-- Query taxonomic data for AIM NPR-A
-- Author: Timm Nawrocki, Alaska Center for Conservation Science
-- Last Updated: 2024-02-06
-- Usage: Script should be executed in a PostgreSQL 14+ database.
-- Description: "Query taxonomic data for AIM NPR-A" queries the accepted taxa found at the BLM AIM NPR-A sites.
-- ---------------------------------------------------------------------------

-- Compile taxon data
SELECT taxon_all.taxon_code as code_akveg
     , taxon_all.taxon_name as taxon_name
     , taxon_status.taxon_status as taxon_status
     , taxon_final.taxon_name as taxon_accepted
	 , taxon_genus_name.taxon_name as taxon_genus
	 , taxon_family.taxon_family as taxon_family
	 , taxon_level.taxon_level as taxon_level
     , taxon_category.taxon_category as taxon_category
     , taxon_habit.taxon_habit as taxon_habit
FROM taxon_all
    LEFT JOIN taxon_status ON taxon_all.taxon_status_id = taxon_status.taxon_status_id
	LEFT JOIN taxon_accepted ON taxon_all.taxon_accepted_code = taxon_accepted.taxon_accepted_code
    LEFT JOIN taxon_all taxon_final ON taxon_accepted.taxon_accepted_code = taxon_final.taxon_code
	LEFT JOIN taxon_level ON taxon_accepted.taxon_level_id = taxon_level.taxon_level_id
	LEFT JOIN taxon_hierarchy ON taxon_accepted.taxon_genus_code = taxon_hierarchy.taxon_genus_code
	LEFT JOIN taxon_all taxon_genus_name ON taxon_accepted.taxon_genus_code = taxon_genus_name.taxon_code
	LEFT JOIN taxon_family ON taxon_hierarchy.taxon_family_id = taxon_family.taxon_family_id
    LEFT JOIN taxon_category ON taxon_hierarchy.taxon_category_id = taxon_category.taxon_category_id
    LEFT JOIN taxon_habit ON taxon_accepted.taxon_habit_id = taxon_habit.taxon_habit_id
ORDER BY taxon_family, taxon_final.taxon_name;