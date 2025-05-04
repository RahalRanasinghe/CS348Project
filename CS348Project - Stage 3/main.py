import pyodbc

DATABASE_CONNECTION = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=synergy-skills-server.database.windows.net,1433;DATABASE=synergy_skills;UID=sqlAdmin;PWD=Synergy!;Encrypt=yes;TrustServerCertificate=no"
try:
    conn = pyodbc.connect(DATABASE_CONNECTION)
    print("Connection successful!")
except Exception as e:
    print("Connection failed:", e)