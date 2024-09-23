import os

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

files_to_read = [
    '/home/gluth/mtg/backend/routes/card_routes.py',
    '/home/gluth/mtg/backend/routes/collection_routes.py',
    '/home/gluth/mtg/backend/routes/kiosk_routes.py',
    '/home/gluth/mtg/backend/routes/set_routes.py'
]

output_file = 'route_contents.txt'

with open(output_file, 'w') as outfile:
    for file_path in files_to_read:
        outfile.write(f"\n\n{'=' * 50}\n")
        outfile.write(f"File: {file_path}\n")
        outfile.write(f"{'=' * 50}\n\n")
        outfile.write(read_file(file_path))

print(f"Contents of the route files have been written to {output_file}")