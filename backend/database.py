from sqlalchemy.engine import URL

DB_PASSWORD = "PUT_YOUR_PASSWORD_HERE"

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=DB_PASSWORD,
    host="localhost",
    port=5432,
    database="university_super_app",
)