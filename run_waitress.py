# run_waitress.py
from waitress import serve
from proyecto_libros.wsgi import application

serve(application, host='0.0.0.0', port=8000)