import os

# Define the files you want to include in the summary
files_to_read = [
    'backend/config.py',
    'backend/database.py',
    'backend/main.py',
    'backend/models/card.py',
    'backend/models/collection.py',
    'backend/models/kiosk.py',
    'backend/models/set.py',
    'backend/routes/__init__.py',
    'backend/routes/card_routes.py',
    'backend/routes/collection_routes.py',
    'backend/routes/kiosk_routes.py',
    'backend/routes/set_routes.py',
    'frontend/.eslintrc.js',
    'frontend/index.html',
    'frontend/vite.config.js',
    'frontend/src/App.vue',
    'frontend/src/main.js',
    'frontend/src/router.js',
    'frontend/src/assets/main.css',
    'frontend/src/components/SetListControls.vue',
    'frontend/src/router/index.js',
    'frontend/src/views/Collection.vue',
    'frontend/src/views/CollectionSetCards.vue',
    'frontend/src/views/Home.vue',
    'frontend/src/views/Import.vue',
    'frontend/src/views/Kiosk.vue',
    'frontend/src/views/SetDetails.vue',
    'frontend/src/views/Sets.vue'
]

# Path to output the combined txt document
output_file = 'project_summary.txt'

# Function to write content to the output file
def write_to_summary(file_path, output_handle):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            output_handle.write(f'== Start of {file_path} ==\n')
            output_handle.write(content)
            output_handle.write(f'\n== End of {file_path} ==\n\n')
    else:
        output_handle.write(f'== {file_path} not found ==\n\n')

# Combine all files into the output text document
with open(output_file, 'w') as summary:
    for file_path in files_to_read:
        write_to_summary(file_path, summary)

print(f"Project summary saved to {output_file}")
