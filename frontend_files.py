frontend_files = [
    '/home/gluth/mtg/frontend/src/assets/main.css',
    '/home/gluth/mtg/frontend/src/components/SetListControls.vue',
    '/home/gluth/mtg/frontend/src/router/index.js',
    '/home/gluth/mtg/frontend/src/views/Collection.vue',
    '/home/gluth/mtg/frontend/src/views/CollectionSetCards.vue',
    '/home/gluth/mtg/frontend/src/views/Home.vue',
    '/home/gluth/mtg/frontend/src/views/Import.vue',
    '/home/gluth/mtg/frontend/src/views/Kiosk.vue',
    '/home/gluth/mtg/frontend/src/views/KioskSetCards.vue',
    '/home/gluth/mtg/frontend/src/views/SetDetails.vue',
    '/home/gluth/mtg/frontend/src/views/Sets.vue',
    '/home/gluth/mtg/frontend/src/App.vue',
    '/home/gluth/mtg/frontend/src/main.js'
]

output_file = '/home/gluth/mtg/frontend_files.txt'

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

with open(output_file, 'w') as f:
    for file_path in frontend_files:
        f.write(f"File: {file_path}\n")
        f.write("=" * 80 + "\n")
        content = read_file_content(file_path)
        f.write(content)
        f.write("\n" + "=" * 80 + "\n\n")

print(f"Frontend file contents have been written to {output_file}")