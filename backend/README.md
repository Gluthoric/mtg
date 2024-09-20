# MTG Collection Kiosk Backend

This is the backend application for the Magic: The Gathering Collection Kiosk project.

## Project Setup

1. Make sure you have [Python](https://www.python.org/) (version 3.7 or higher) installed on your system.

2. It's recommended to use a virtual environment. Create and activate one using:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Environment variables are already set up in the `.env` file in the `refactor/backend` directory. The file contains:

   ```
   DATABASE_URI=postgresql://postgres.xbuiunafhcscvjftnvxr:Timothy2-Sample-Underwent@aws-0-us-west-1.pooler.supabase.com:6543/postgres?sslmode=require
   SECRET_KEY=you-will-never-guess
   ```

   If you need to modify these values:
   - Update the `DATABASE_URI` if you're using a different Supabase project or database.
   - Change the `SECRET_KEY` to a different secure random string of your choice.

## Running the Development Server

To start the development server, run:

```
python main.py
```

This will start the Flask development server, usually at `http://localhost:5000`.

## Database Initialization

The application is set up to automatically initialize the database when you run `main.py`. Here's how it works:

- When you start the application, it checks if the database tables already exist.
- If the tables don't exist (i.e., it's a fresh installation), it will create all necessary tables.
- If the tables already exist, it won't make any changes to the database structure.

This approach ensures that your existing data is not overwritten when you start the application. However, it's important to note that this method doesn't handle database migrations. If you make changes to your database models, you'll need to manually update your database schema or use a migration tool like Alembic.

## Project Structure

- `main.py`: The main entry point of the application
- `config.py`: Configuration settings
- `models/`: Database models
- `routes/`: API route definitions
- `database.py`: Database connection and session management
- `.env`: Environment variables (including database connection details)

## API Endpoints

- `/api/cards`: Card-related operations
- `/api/sets`: Set-related operations
- `/api/collection`: Collection management
- `/api/kiosk`: Kiosk inventory management
- `/api/import`: Card import operations

For detailed API documentation, refer to the inline comments in the route files.

## Database

This project uses SQLAlchemy with PostgreSQL, connected to a Supabase instance. The connection details are managed through the `DATABASE_URI` environment variable in the `.env` file.

## Additional Notes

- This project uses Flask as the web framework and SQLAlchemy as the ORM.
- Make sure to handle CORS appropriately when connecting with the frontend.
- Always keep your `SECRET_KEY` and database credentials secure and never commit them to version control.

For more information on Flask and SQLAlchemy, check out the [Flask documentation](https://flask.palletsprojects.com/) and [SQLAlchemy documentation](https://docs.sqlalchemy.org/).