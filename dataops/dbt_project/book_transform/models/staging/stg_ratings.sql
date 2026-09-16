{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM raw_data.ratings
)

SELECT
    user_id,
    isbn,
    book_rating
FROM source
WHERE user_id IS NOT NULL
  AND isbn IS NOT NULL
  AND book_rating IS NOT NULL