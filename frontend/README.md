# MTG Collection Kiosk Frontend

This is the frontend application for the Magic: The Gathering Collection Kiosk project.

## Project Setup

1. Make sure you have [Node.js](https://nodejs.org/) (version 14 or higher) installed on your system.

2. Navigate to the frontend directory:

   ```
   cd refactor/frontend
   ```

3. Install the project dependencies:

   ```
   npm install
   ```

4. Create a `.env` file in the root of the frontend directory with the following content:

   ```
   VITE_API_URL=http://localhost:5000
   ```

   Adjust the URL if your backend is running on a different port or host.

## Development

To start the development server:

```
npm run dev
```

This will start the Vite development server, usually at `http://localhost:5173`. You can access the application in your web browser at this address.

## Building for Production

To create a production build:

```
npm run build
```

This will create a `dist` folder with the compiled and minified assets ready for deployment.

## Linting

To lint and fix files:

```
npm run lint
```

## Project Structure

- `src/components/`: Reusable Vue components
- `src/views/`: Vue components that represent pages or views in the application
- `src/router/`: Vue Router configuration
- `src/assets/`: Static assets like images and global CSS
- `src/main.js`: The main entry point of the application

## Additional Notes

- This project uses Vue 3, Vue Router for routing, and Axios for making HTTP requests to the backend API.
- Make sure the backend server is running and accessible at the URL specified in the `VITE_API_URL` environment variable.

For more information on Vue.js and Vite, check out the [Vue.js documentation](https://v3.vuejs.org/) and [Vite documentation](https://vitejs.dev/).
