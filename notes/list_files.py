import os

files_to_list = [
    '/home/gluth/mtg/frontend/src/assets/main.css',
    '/home/gluth/mtg/frontend/src/components',
    '/home/gluth/mtg/frontend/src/components/SetListControls.vue',
    '/home/gluth/mtg/frontend/src/router',
    '/home/gluth/mtg/frontend/src/router/index.js',
    '/home/gluth/mtg/frontend/src/views',
    '/home/gluth/mtg/frontend/src/views/Collection.vue',
    '/home/gluth/mtg/frontend/src/views/CollectionSetCards.vue',
    '/home/gluth/mtg/frontend/src/views/Home.vue',
    '/home/gluth/mtg/frontend/src/views/Import.vue',
    '/home/gluth/mtg/frontend/src/views/Kiosk.vue',
    '/home/gluth/mtg/frontend/src/views/QuantityControl.vue',
    '/home/gluth/mtg/frontend/src/views/SetDetails.vue',
    '/home/gluth/mtg/frontend/src/views/Sets.vue',
    '/home/gluth/mtg/frontend/src/App.vue',
    '/home/gluth/mtg/frontend/src/main.js'
]

with open('file_contents.txt', 'w') as output_file:
    for file_path in files_to_list:
        output_file.write(f"\n{'='*50}\n")
        output_file.write(f"File: {file_path}\n")
        output_file.write(f"{'='*50}\n\n")

        if os.path.isdir(file_path):
            output_file.write(f"[This is a directory]\n")
        else:
            try:
                with open(file_path, 'r') as input_file:
                    content = input_file.read()
                    output_file.write(content)
            except Exception as e:
                output_file.write(f"[Error reading file: {str(e)}]\n")

        output_file.write("\n")

print("File contents have been written to file_contents.txt")