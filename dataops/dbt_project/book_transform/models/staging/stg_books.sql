{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM raw_data.books
)

SELECT
    isbn,
    book_title,
    COALESCE(book_author, 'Unknown') AS book_author,
    TRY_CAST(year_of_publication AS INTEGER) AS year_of_publication,
    COALESCE(publisher, 'Unknown') AS publisher
FROM source
WHERE isbn IS NOT NULL
  AND book_title IS NOT NULL