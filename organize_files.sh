#!/bin/bash

# Remove the existing combined.md if it exists
rm -f combined.md

# Read each line from changes.md
while IFS= read -r file_path; do
    echo "Read line: $file_path" >&2
    echo "Processing file: $file_path" >&2

    # Add the file path as a header
    echo "# $file_path" >> combined.md

    # Add the file contents
    echo '```' >> combined.md
    if [ -f "$file_path" ]; then
        if [ -r "$file_path" ]; then
            cat "$file_path" >> combined.md
        else
            echo "File not readable: $file_path" >> combined.md
            echo "File not readable: $file_path" >&2
        fi
    else
        echo "File not found: $file_path" >> combined.md
        echo "File not found: $file_path" >&2
    fi
    echo '```' >> combined.md

    # Add a newline for separation
    echo "" >> combined.md
done < changes.md

echo "Combined file created: combined.md"