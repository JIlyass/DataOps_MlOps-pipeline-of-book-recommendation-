{{ config(materialized='table') }}

-- Jointure entre ratings explicites et informations livres
SELECT
    r.user_id,
    r.isbn,
    r.book_rating,
    b.book_title,
    b.book_author,
    b.publisher,
    b.year_of_publication
FROM {{ ref('ratings_explicit') }} AS r
INNER JOIN {{ ref('stg_books') }} AS b
    ON r.isbn = b.isbn