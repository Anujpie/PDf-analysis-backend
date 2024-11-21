from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2 import sql
import io

app = FastAPI()

# PostgreSQL database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="pdf-analyse-db",
        user="postgres",  # your PostgreSQL username
        password="admin#123",  # your PostgreSQL password
        host="localhost",  # or the host of your PostgreSQL instance
        port="5432"  # default PostgreSQL port
    )

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    # Read the file content
    file_content = await file.read()

    # Open a connection to the PostgreSQL database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Insert the file into the database
        insert_query = sql.SQL("INSERT INTO Document (pdf_file) VALUES (%s)")
        cursor.execute(insert_query, (file.filename, file_content))
        connection.commit()

        return JSONResponse(content={"message": "File uploaded successfully!"}, status_code=200)
    except Exception as e:
        connection.rollback()
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)
    finally:
        cursor.close()
        connection.close()

