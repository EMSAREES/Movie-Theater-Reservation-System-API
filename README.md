# Movie-Theater-Reservation-System-API

It is a movie reservation system created with the goal of trying to learn more about Flask.

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