#!/bin/bash
# Usage: ./batch_recreate_cogs.sh cog_assets.csv

CSV_FILE=$1

if [ -z "$CSV_FILE" ]; then
    echo "Usage: $0 <csv_file>"
    exit 1
fi

# Skip header line and read CSV
tail -n +2 "$CSV_FILE" | while IFS=, read -r asset_id type uri
do
    # Remove carriage return if present (handles Windows-style CSVs)
    uri=$(echo "$uri" | tr -d '\r')
    asset_id=$(echo "$asset_id" | tr -d '\r')
    type=$(echo "$type" | tr -d '\r')
    
    echo "----------------------------------------------------------------"
    echo "Processing $asset_id ($type)..."
    python3 recreate_cog_assets.py --asset_id "$asset_id" --type "$type" --uri "$uri" --force
done