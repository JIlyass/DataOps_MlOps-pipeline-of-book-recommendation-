{{ config(materialized='table') }}

-- Top livres par nombre de ratings explicites (baseline popularité)
SELECT
    book_title,
    book_author,
    COUNT(*) AS num_ratings,
    ROUND(AVG(book_rating), 2) AS avg_rating
FROM {{ ref('books_enriched') }}
GROUP BY book_title, book_author
ORDER BY num_ratings DESC