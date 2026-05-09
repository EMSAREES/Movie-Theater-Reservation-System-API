# Movie-Theater-Reservation-System-API

This is a movie reservation system created to learn more about Flask. I'm not sure if I'm using the correct structure or dependency, but this is the first test.

-----------------------------------------------------------------------------
> **Note:** This table represents the initial idea of the available endpoints.  
> It may not be final — endpoints could be added, modified, or removed as the project evolves.

# User
| Method | Endpoint | Description |
| --- | --- | --- |
| POST | ``/api/v1/users/register`` | Register a new user |
| POST | ``/api/v1/users/login`` | User login |

# Movie
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | ``/api/v1/movies`` | List movies with pagination and filters |
| GET | ``/api/v1/movies/:id`` | Get movie by ID |
| POST | ``/api/v1/movies`` | Create a new movie |
| PUT | ``/api/v1/movies/:id`` | Update movie |
| DELETE | ``/api/v1/movies/:id`` | Delete movie |

# Room
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | ``/api/v1/rooms`` | List all rooms |
| GET | ``/api/v1/rooms/:id`` | Get room by ID |
| POST | ``/api/v1/rooms`` | Create a new room |
| PUT | ``/api/v1/rooms/:id`` | Update room |

# Screenings
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | ``/api/v1/screenings`` | List screenings |
| GET | ``/api/v1/screenings/:id`` | Get screening by ID |
| GET | ``/api/v1/screenings/:id/seats`` | View available seats |
| POST | ``/api/v1/screenings`` | Create a new screening |
| PUT | ``/api/v1/screenings/:id`` | Update screening |

# TICKETS
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | ``/api/v1/tickets`` | List tickets |
| GET | ``/api/v1/tickets/:id`` | Get ticket by ID |
| POST | ``/api/v1/tickets`` | Create reservation |
| DELETE | ``/api/v1/tickets/:id`` | Cancel reservation |


> v1 =  Version one. "Because I felt like it."

--------------------------------------------------------------------------------
# structure
The current project uses a layered architecture inspired by Clean Architecture, with the goal of learning and mastering the fundamentals of separation of responsibilities.
In future projects, I plan to adopt a modular architecture, which is more recommended for scalable applications and facilitates organization by domains or functionalities.

REQUEST HTTP
    │
    ▼
[ROUTES]         
    │
    ▼
[CONTROLLER]     
    │
    ▼
[SERVICE]      
    │
    ▼
[REPOSITORY]      
    │
    ▼
[MODEL/DB]      

-------------------------------------------------------------------------------
# virtual environment commands
1. Create a virtual environment
> python -m venv venv
This command creates a folder named venv containing a clean Python environment.

It ensures that all packages installed (via pip) are scoped only to this project.

Recommended because it prevents version conflicts and keeps your global Python installation clean.

2. Activate the virtual environment
> .\venv\Scripts\Activate.ps1
This activates the virtual environment in PowerShell.

Once activated, your terminal prompt will show (venv) at the beginning, meaning you’re working inside the isolated environment.

All subsequent Python and pip commands will use this environment.

3. Deactivate when finished
> deactivate
This exits the virtual environment and returns you to your global Python installation.

Recommendation: Always create and activate a virtual environment before installing dependencies (pip install -r requirements.txt). This keeps your project reproducible and avoids dependency issues.

---------------------------------------------------------------------------
# Dependencies
| Library | Purpose |
| --- | --- |
| **flask** | The main web framework. Handles HTTP routes, requests, and responses. |
| **flask-sqlalchemy** | ORM — allows working with the database using Python classes instead of raw SQL. |
| **flask-migrate** | Manages changes in the database structure (migrations). |
| **psycopg2-binary** | The “bridge” between Python and PostgreSQL. |
| **marshmallow** | Serialization/Deserialization — converts Python objects to JSON and validates data. |
| **python-dotenv** | Reads environment variables from ``.env`` files. |
| **flask-jwt-extended** | Authentication using JWT tokens. |
| **bcrypt** | Securely encrypts passwords. |
| **flask-cors** | Allows frontends from other domains to consume the API. |

-------------------------------------------------------------------------------
# .env — Environment variables
> NEVER upload this file to GitHub

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME= name of DB
DB_USER=postgres
DB_PASSWORD= you password

# JWT
JWT_SECRET_KEY= Clava_ultra_mamalona_Mega_Secreta
JWT_ACCESS_TOKEN_EXPIRES=3600