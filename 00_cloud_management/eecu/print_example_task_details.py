import ee
import json

# Initialize with your project
ee.Initialize(project='akveg-map')

# Fetch tasks
tasks = ee.data.listOperations()

for task in tasks:
    meta = task.get('metadata', {})
    description = meta.get('description', '')
    
    # Target the specific tasks you are looking for
    if 's2_dw_counts' in description:
        print("--- DIAGNOSTIC: FOUND TASK ---")
        print(f"Description: {description}")
        print(f"State: {meta.get('state')}")
        
        # Print the entire metadata dictionary to find the hidden key
        print("\nFull Metadata Dictionary (Look for '939.1158' here):")
        print(json.dumps(meta, indent=2))
        
        # Stop after one result to keep the output clean
        break