select
    source_file,
    sha256
from {{ source('noaa', 'file_manifest') }}
where
    length(sha256) <> 64
    or not regexp_full_match(sha256, '[0-9a-f]{64}')