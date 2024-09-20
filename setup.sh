#!/bin/bash

# Exit on error
set -e

echo "Setting up MTG Collection Kiosk..."

# Setup Backend
echo "Setting up backend..."
cd refactor/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..

# Setup Frontend
echo "Setting up frontend..."
cd refactor/frontend
npm install
cd ../..

echo "Setup complete!"
echo "To run the backend:"
echo "  cd refactor/backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "To run the frontend:"
echo "  cd refactor/frontend"
echo "  npm run serve"
echo ""
echo "Make sure to set up your .env files in both frontend and backend directories!"