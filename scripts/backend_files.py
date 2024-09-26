backend_files = [
    '/home/gluth/mtg/backend/config.py',
    '/home/gluth/mtg/backend/database.py',
    '/home/gluth/mtg/backend/main.py',
    '/home/gluth/mtg/backend/README.md',
    '/home/gluth/mtg/backend/requirements.txt',
    '/home/gluth/mtg/backend/models/card.py',
    '/home/gluth/mtg/backend/models/collection.py',
    '/home/gluth/mtg/backend/models/kiosk.py',
    '/home/gluth/mtg/backend/models/set.py',
    '/home/gluth/mtg/backend/routes/__init__.py',
    '/home/gluth/mtg/backend/routes/card_routes.py',
    '/home/gluth/mtg/backend/routes/collection_routes.py',
    '/home/gluth/mtg/backend/routes/kiosk_routes.py',
    '/home/gluth/mtg/backend/routes/set_routes.py'
]

output_file = '/home/gluth/mtg/backend_files.txt'

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

with open(output_file, 'w') as f:
    for file_path in backend_files:
        f.write(f"File: {file_path}\n")
        f.write("=" * 80 + "\n")
        content = read_file_content(file_path)
        f.write(content)
        f.write("\n" + "=" * 80 + "\n\n")

print(f"Backend file contents have been written to {output_file}")