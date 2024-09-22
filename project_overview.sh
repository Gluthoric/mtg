#!/bin/bash

# Exit on error
set -e

echo "Generating project overview..."
{
    echo "# Project Overview"
    echo ""
    echo "## Backend"

    echo "### Models"
    for file in backend/models/{card,collection,kiosk,set}.py; do
        echo "#### $file"
        echo '```python'
        cat "$file"
        echo '```'
        echo ""
    done

    echo "### Routes"
    for file in backend/routes/{__init__,card_routes,collection_routes,kiosk_routes,set_routes}.py; do
        echo "#### $file"
        echo '```python'
        cat "$file"
        echo '```'
        echo ""
    done

    echo "### Other Backend Files"
    for file in backend/{config,database,main}.py; do
        echo "#### $file"
        echo '```python'
        cat "$file"
        echo '```'
        echo ""
    done

    echo "## Frontend"

    echo "### Components"
    echo "#### frontend/src/components/SetListControls.vue"
    echo '```vue'
    cat frontend/src/components/SetListControls.vue
    echo '```'
    echo ""

    echo "### Views"
    for file in frontend/src/views/{Collection,Home,Import,Kiosk,SetDetails,Sets}.vue; do
        echo "#### $file"
        echo '```vue'
        cat "$file"
        echo '```'
        echo ""
    done

    echo "### Other Frontend Files"
    echo "#### frontend/src/assets/main.css"
    echo '```css'
    cat frontend/src/assets/main.css
    echo '```'
    echo ""

    echo "#### frontend/src/router/index.js"
    echo '```javascript'
    cat frontend/src/router/index.js
    echo '```'
    echo ""

    echo "#### frontend/src/App.vue"
    echo '```vue'
    cat frontend/src/App.vue
    echo '```'
    echo ""

    echo "#### frontend/src/main.js"
    echo '```javascript'
    cat frontend/src/main.js
    echo '```'
    echo ""

    echo "#### frontend/src/router.js"
    echo '```javascript'
    cat frontend/src/router.js
    echo '```'
    echo ""

} > project_overview.txt

echo "Project overview with file contents has been written to project_overview.txt"