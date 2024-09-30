# MTG Collection Kiosk Backend

This is the backend application for the Magic: The Gathering Collection Kiosk project.

## Project Setup

1. Make sure you have [Python](https://www.python.org/) (version 3.7 or higher) installed on your system.

2. Install [Redis](https://redis.io/download) on your system. It's used for caching to improve performance.

3. It's recommended to use a virtual environment. Create and activate one using:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

5. Environment variables are already set up in the `.env` file in the `refactor/backend` directory. The file contains:

   ```
   DATABASE_URI=postgresql://postgres.xbuiunafhcscvjftnvxr:Timothy2-Sample-Underwent@aws-0-us-west-1.pooler.supabase.com:6543/postgres?sslmode=require
   SECRET_KEY=you-will-never-guess
   REDIS_URL=redis://localhost:6379/0
   ```

   If you need to modify these values:
   - Update the `DATABASE_URI` if you're using a different Supabase project or database.
   - Change the `SECRET_KEY` to a different secure random string of your choice.
   - Update the `REDIS_URL` if your Redis server is not running on the default localhost:6379.

## Running the Development Server

To start the development server, run:

```
python main.py
```

This will start the Flask development server, usually at `http://localhost:5000`.

Make sure your Redis server is running before starting the application.

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

## Performance Optimizations

The backend has been optimized for better performance, particularly focusing on the collection-related routes:

1. **Caching with Redis**: Frequently accessed data is cached using Redis, reducing database load and improving response times. The cache is automatically invalidated when data is updated. This includes:
   - Collection data
   - Collection sets data
   - Collection statistics
   - Set cards in the collection

2. **Efficient Serialization**: The `orjson` library is used for faster JSON serialization and deserialization, particularly beneficial for large datasets.

3. **Query Optimization**: Database queries have been optimized to reduce the load on the database and improve response times.

4. **Pagination**: All list endpoints support pagination to handle large datasets efficiently.

5. **Cache Invalidation**: When data is updated (e.g., adding or removing cards from the collection), related caches are automatically invalidated to ensure data consistency.

These optimizations significantly improve the application's performance, especially when dealing with large collections or high traffic.

## Additional Notes

- This project uses Flask as the web framework and SQLAlchemy as the ORM.
- Make sure to handle CORS appropriately when connecting with the frontend.
- Always keep your `SECRET_KEY` and database credentials secure and never commit them to version control.

For more information on Flask and SQLAlchemy, check out the [Flask documentation](https://flask.palletsprojects.com/) and [SQLAlchemy documentation](https://docs.sqlalchemy.org/).