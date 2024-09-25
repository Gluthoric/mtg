from supabase sql editor :

List Indexes for sets:

SELECT
  i.relname AS index_name,
  a.attname AS column_name,
  ix.indisunique AS is_unique,
  ix.indisprimary AS is_primary
FROM
  pg_index ix
  JOIN pg_class t ON t.oid = ix.indrelid
  JOIN pg_class i ON i.oid = ix.indexrelid
  JOIN pg_attribute a ON a.attnum = ANY (ix.indkey)
  AND a.attrelid = t.oid
WHERE
  t.relname = 'sets'
ORDER BY
  i.relname;

| index_name                        | column_name | is_unique | is_primary |
| --------------------------------- | ----------- | --------- | ---------- |
| idx_39037_sqlite_autoindex_sets_1 | id          | true      | false      |
| idx_39037_sqlite_autoindex_sets_2 | code        | true      | false      |
| idx_sets_set_type                 | set_type    | false     | false      |


List Indexes for collections

SELECT
  i.relname AS index_name,
  a.attname AS column_name,
  ix.indisunique AS is_unique,
  ix.indisprimary AS is_primary
FROM
  pg_index ix
  JOIN pg_class t ON t.oid = ix.indrelid
  JOIN pg_class i ON i.oid = ix.indexrelid
  JOIN pg_attribute a ON a.attnum = ANY (ix.indkey)
  AND a.attrelid = t.oid
WHERE
  t.relname = 'collections'
ORDER BY
  i.relname;

  | index_name                 | column_name | is_unique | is_primary |
| -------------------------- | ----------- | --------- | ---------- |
| idx_39023_collections_pkey | id          | true      | false      |
| idx_collection_card_id     | card_id     | false     | false      |
| idx_collections_card_id    | card_id     | false     | false      |


List Indexes for kiosk

SELECT
  i.relname AS index_name,
  a.attname AS column_name,
  ix.indisunique AS is_unique,
  ix.indisprimary AS is_primary
FROM
  pg_index ix
  JOIN pg_class t ON t.oid = ix.indrelid
  JOIN pg_class i ON i.oid = ix.indexrelid
  JOIN pg_attribute a ON a.attnum = ANY (ix.indkey)
  AND a.attrelid = t.oid
WHERE
  t.relname = 'kiosk'
ORDER BY
  i.relname;



  | index_name           | column_name | is_unique | is_primary |
| -------------------- | ----------- | --------- | ---------- |
| idx_39030_kiosk_pkey | id          | true      | false      |
| idx_kiosk_card_id    | card_id     | false     | false      |

List Indexes for cards

SELECT
  i.relname AS index_name,
  a.attname AS column_name,
  ix.indisunique AS is_unique,
  ix.indisprimary AS is_primary
FROM
  pg_index ix
  JOIN pg_class t ON t.oid = ix.indrelid
  JOIN pg_class i ON i.oid = ix.indexrelid
  JOIN pg_attribute a ON a.attnum = ANY (ix.indkey)
  AND a.attrelid = t.oid
WHERE
  t.relname = 'cards'
ORDER BY
  i.relname;


  | index_name         | column_name | is_unique | is_primary |
| ------------------ | ----------- | --------- | ---------- |
| cards_pkey         | id          | true      | true       |
| idx_cards_id       | id          | false     | false      |
| idx_cards_set_code | set_code    | false     | false      |
| unique_cards_id    | id          | true      | false      |