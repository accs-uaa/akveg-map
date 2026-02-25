#!/bin/bash

# Fetch matching buckets
buckets=$(gcloud storage buckets list --format="value(name)" --filter="name ~ akveg-data")

# Helper to sum raw bytes
sum_bytes() {
    awk '{ sum += $1 } END { printf "%.0f", sum }'
}

# Helper to format bytes
format_bytes() {
    local sum=$1
    awk -v sum="$sum" 'BEGIN {
        if (sum == 0) { print "0 B" }
        else if (sum < 1024) { printf "%d B", sum }
        else if (sum < 1048576) { printf "%.2f KiB", sum/1024 }
        else if (sum < 1073741824) { printf "%.2f MiB", sum/1048576 }
        else if (sum < 1099511627776) { printf "%.2f GiB", sum/1073741824 }
        else { printf "%.2f TiB", sum/1099511627776 }
    }'
}

printf "%-35s | %-50s | %-15s\n" "Bucket" "Top-Level Folder" "Size"
printf "%-35s | %-50s | %-15s\n" "-----------------------------------" "--------------------------------------------------" "---------------"

for bucket in $buckets; do
    
    # 1. Get ONLY the top-level folder paths (prefixes) ending in a slash
    folders=$(gsutil ls "gs://${bucket}/" 2>/dev/null | grep "/$")
    
    # Temp file for sorting
    tmp_file=$(mktemp)

    for folder in $folders; do
        # 2. List every individual nested file with '**' and sum the raw bytes.
        # Bypassing the '-s' summary flag guarantees we capture all nested data accurately.
        raw_size=$(gsutil du "${folder}**" 2>/dev/null | sum_bytes)
        
        # Clean up the folder name for display
        folder_clean=$(echo "$folder" | sed "s|gs://${bucket}/||")
        
        echo "$raw_size $folder_clean" >> "$tmp_file"
    done
    
    # Sort by size (numeric) and print
    sort -n -k1 "$tmp_file" | while read -r size folder_clean; do
        formatted_size=$(format_bytes "$size")
        printf "%-35s | %-50s | %-15s\n" "$bucket" "$folder_clean" "$formatted_size"
    done
    rm "$tmp_file"

    # 3. Get the grand total for the bucket using the exact same raw-byte method
    bucket_total_raw=$(gsutil du "gs://${bucket}/**" 2>/dev/null | sum_bytes)
    bucket_total=$(format_bytes "$bucket_total_raw")
    
    printf "%-35s | %-50s | %-15s\n" "" "TOTAL for $bucket" "$bucket_total"
    echo "--------------------------------------------------------------------------------------------------------"
done
