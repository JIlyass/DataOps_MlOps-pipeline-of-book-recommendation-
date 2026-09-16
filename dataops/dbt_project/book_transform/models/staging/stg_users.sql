{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM raw_data.users
)

SELECT
    user_id,
    location,
    -- On garde l'âge tel quel, le remplissage se fera dans un modèle mart
    CASE
        WHEN age IS NULL OR age < 5 OR age > 100 THEN NULL
        ELSE age
    END AS age
FROM source
WHERE user_id IS NOT NULL