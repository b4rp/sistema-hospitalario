
# 🏥⚕️ Sistema de Gestión Hospitalaria

Proyecto universitario para la gestión integral de pacientes, médicos, citas, diagnósticos, tratamientos, historiales y atenciones en un hospital. Desarrollado en Python con Streamlit y SQLite.

## Características

- Registro y gestión de pacientes y médicos
- Agendamiento y control de citas médicas
- Registro de diagnósticos y tratamientos
- Historial médico completo por paciente
- Gestión de atenciones y seguimiento
- Interfaz web amigable y accesible con Streamlit
- Base de datos relacional en SQLite
- Búsqueda avanzada, insensible a tildes y por ID
- Datos de prueba automáticos para desarrollo

## Estructura del proyecto

```
V2.6/
├── app.py                      # Entrada principal de la app Streamlit
├── hospital.sql                # Script SQL con el esquema de la base de datos
├── requirements.txt            # Dependencias del proyecto
├── scripts/
│   └── datos_pruebas.py        # Script para poblar la base con datos de prueba
├── modulos/
│   ├── db/                     # Lógica de acceso a datos
│   └── ui/                     # Interfaz Streamlit por módulo
└── README.md
```

## Instalación

1. **Clona el repositorio**
   ```sh
   git clone <url-del-repo>
   cd V2.6
   ```

2. **Instala dependencias**
   ```sh
   pip install -r requirements.txt
   ```

3. **Crea la base de datos**
   ```sh
   sqlite3 hospital.db < hospital.sql
   ```

4. **Pobla la base con datos de prueba**
   ```sh
   python scripts/datos_pruebas.py
   ```

## Uso

1. **Inicia la aplicación**
   ```sh
   streamlit run app.py
   ```

2. **Accede desde el navegador**
   - URL por defecto: [http://localhost:8501](http://localhost:8501)

3. **Navega por las secciones**
   - Pacientes, Médicos, Citas, Diagnósticos, Tratamientos, Historiales, Atenciones, Especialidades.

## Requisitos

- Python 3.12+
- Streamlit >= 1.39.0
- pandas >= 2.1.0
- cryptography >= 41.0.0
- SQLite3

## Notas técnicas

- El sistema valida relaciones entre entidades (por ejemplo, no se puede eliminar un diagnóstico si tiene tratamientos asociados).
- Los módulos en `modulos/db` gestionan la lógica de acceso a datos.
- Los módulos en `modulos/ui` implementan la interfaz Streamlit para cada entidad.
- El script de datos de prueba genera registros realistas y relaciones válidas.
- Todas las búsquedas son insensibles a tildes y permiten filtrar por ID.

## Accesibilidad

- Todos los widgets Streamlit tienen etiquetas descriptivas para cumplir con buenas prácticas de accesibilidad.

## 🧙🏻‍♂️ Autores

- Matías Bórquez
- Benjamín Rivera

## Licencia

Este proyecto es de uso académico. Puedes modificarlo y adaptarlo libremente para fines educativos.
