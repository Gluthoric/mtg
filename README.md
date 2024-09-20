# MTG Collection Kiosk

MTG Collection Kiosk is a web application for managing Magic: The Gathering card collections and kiosk inventories. It allows users to track their card collections, manage kiosk inventories, and import card data.

## Project Structure

The project is divided into two main parts:

1. Frontend (Vue.js application)
2. Backend (Flask API)

### Frontend

Located in the `refactor/frontend` directory, the frontend is a Vue.js application that provides the user interface for the MTG Collection Kiosk.

For more details on setting up and running the frontend, see the [Frontend README](refactor/frontend/README.md).

### Backend

Located in the `refactor/backend` directory, the backend is a Flask application that serves as the API for the MTG Collection Kiosk.

For more details on setting up and running the backend, see the [Backend README](refactor/backend/README.md).

## Getting Started

To get the project up and running, you'll need to set up both the frontend and backend:

1. Clone this repository:
   ```
   git clone https://github.com/your-username/mtg-collection-kiosk.git
   cd mtg-collection-kiosk
   ```

2. Set up and run the backend:
   ```
   cd refactor/backend
   # Follow the instructions in the backend README.md
   ```

3. In a new terminal, set up and run the frontend:
   ```
   cd refactor/frontend
   # Follow the instructions in the frontend README.md
   ```

4. Access the application by opening a web browser and navigating to the URL where the frontend is being served (typically `http://localhost:5173`).

## Features

- View and manage card collections
- Manage kiosk inventory
- Browse Magic: The Gathering sets and cards
- Import cards via CSV or individual entries
- Search and filter cards and sets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Magic: The Gathering and all related properties are owned by Wizards of the Coast
- This project uses data from Scryfall but is not endorsed or approved by Scryfall