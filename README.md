# Movie-Theater-Reservation-System-API

It is a movie reservation system created with the goal of trying to learn more about Flask.

-----------------------------------------------------------------------------
> **Note:** This table represents the initial idea of the available endpoints.  
> It may not be final — endpoints could be added, modified, or removed as the project evolves.

# USUARIOS
POST   /api/v1/users/register
POST   /api/v1/users/login

# PELÍCULAS
GET    /api/v1/movies           (list with pagination and filters)
GET    /api/v1/movies/:id
POST   /api/v1/movies
PUT    /api/v1/movies/:id
DELETE /api/v1/movies/:id

# SALAS
GET    /api/v1/rooms
GET    /api/v1/rooms/:id
POST   /api/v1/rooms
PUT    /api/v1/rooms/:id

# FUNCIONES
GET    /api/v1/screenings
GET    /api/v1/screenings/:id
GET    /api/v1/screenings/:id/seats    (seats available)
POST   /api/v1/screenings
PUT    /api/v1/screenings/:id

# TICKETS
GET    /api/v1/tickets
GET    /api/v1/tickets/:id
POST   /api/v1/tickets              (create reservation)
DELETE /api/v1/tickets/:id          (cancel reservation)


> v1 =  Version one. "Because I felt like it."

--------------------------------------------------------------------------------
# structure
El plan consiste en utilizar una "arquitectura por capas basada en una arquitectura limpia".