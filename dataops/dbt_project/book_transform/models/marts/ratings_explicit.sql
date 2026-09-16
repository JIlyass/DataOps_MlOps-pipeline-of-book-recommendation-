{{ config(materialized='table') }}

-- Ratings explicites uniquement (1 à 10), comme dans le notebook
SELECT
    user_id,
    isbn,
    book_rating
FROM {{ ref('stg_ratings') }}
WHERE book_rating BETWEEN 1 AND 10