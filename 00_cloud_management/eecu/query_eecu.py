import ee

# Initialize with your project
ee.Initialize(project='akveg-map')

# Fetch the tasks
tasks = ee.data.listOperations()

total_eecu_seconds = 0.0
task_count = 0

for task in tasks:
    meta = task.get('metadata', {})
    description = meta.get('description', '')
    state = meta.get('state', '')

    # Filter for your specific tasks
    if 's2_dw_counts' in description and state == 'SUCCEEDED':
        # Use the key confirmed by your diagnostic script
        usage = meta.get('batchEecuUsageSeconds', 0.0)
        total_eecu_seconds += usage
        task_count += 1

total_eecu_hours = total_eecu_seconds / 3600

print(f"Total Tasks Found: {task_count}")
print(f"Total EECU-seconds: {total_eecu_seconds:.4f}")
print(f"Total EECU-hours: {total_eecu_hours:.4f}")