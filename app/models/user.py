import bcrypt
from datetime import datetime, timezone
from app import db

class User(db.Model):

    __tablename__ = 'users' # nombre de la tabla

    # ── Columnas ───────────────────────────────────────────────────────────── 

    # Clave primaria — identificador único autoincremental
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # nullable=False → No puede ser NULL en la BD (campo obligatorio)
    # unique=True → No pueden existir dos filas con el mismo valor
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)

    # index=True en email porque buscaremos usuarios por email frecuentemente
    # Un índice acelera las búsquedas (como el índice de un libro)
    
    # La contraseña NUNCA se guarda en texto plano
    # Guardamos el hash bcrypt que tiene longitud fija de 60 chars
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Rol del usuario — usamos un valor por defecto
    role = db.Column(db.String(50), nullable=False, default='customer')
    
    # Soft delete: en vez de borrar, marcamos como inactivo
    # Esto preserva la integridad referencial y el historial
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Timestamps — cuándo se creó y cuándo se modificó por última vez
    # server_default: el valor lo asigna PostgreSQL, no Python
    # onupdate: se actualiza automáticamente al modificar el registro
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ── Relaciones ────────────────────────────────────────────────────────────

    # Un usuario puede tener muchos tickets
    # backref crea automáticamente ticket.user (acceso inverso)
    # lazy='dynamic' no carga los tickets hasta que los pedimos explícitamente
    tickets = db.relationship(
        'Ticket',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # ── Métodos de instancia ──────────────────────────────────────────────────

    def set_password(self, password: str) -> None:
        """
        Encripta y guarda la contraseña usando bcrypt.
        
        bcrypt es el algoritmo recomendado para contraseñas porque:
        1. Es lento intencionalmente (dificulta ataques de fuerza bruta)
        2. Incluye un "salt" aleatorio (cada hash es único)
        3. El hash incluye el salt (no necesitamos guardarlo separado)
        
        NUNCA: self.password = password  ← PELIGROSO
        SIEMPRE: self.set_password(password)
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        Verifica si la contraseña proporcionada coincide con el hash guardado.
        
        Returns:
            bool: True si la contraseña es correcta, False si no
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    @property
    def full_name(self) -> str:
        """Nombre completo como propiedad calculada."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """
        Representación básica como diccionario.
        NOTA: Nunca incluir password_hash aquí.
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active
        }
    
    def __repr__(self) -> str:
        """Representación para debugging en consola."""
        return f'<User {self.id}: {self.email}>'

"""
Modelo de Usuario.

Un modelo SQLAlchemy es una clase Python que representa
una tabla en la base de datos. Cada atributo de clase
es una columna en la tabla.

¿Qué es SQLAlchemy ORM?
ORM = Object-Relational Mapping
Nos permite trabajar con la BD usando Python puro,
sin escribir SQL directamente (aunque podemos si queremos).

En vez de:
    SELECT * FROM users WHERE id = 1;

Escribimos:
    User.query.get(1)
"""