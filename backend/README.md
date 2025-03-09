# How To: Backend

## Requirements (Debian Linux)


- Python 3.6+
```bash
sudo apt update
sudo apt install python3
```
- Pip
```bash
sudo apt install python3-pip
```
- Venv (use your python version)
```bash
sudo apt install python3.8-venv
```

## Installation

- Una vez clonado el repositorio se deberá ejecutar los siguientes comandos desde la raíz del proyecto.

### Crear virtual enviroment y activarlo 
- (si python no funciona usar python3)
```bash
python -m venv .venv
source .venv/bin/activate
```
-  Al terminar de usar el virtual enviroment podremos desactivarlo con `deactivate`

### Instalar requisitos
```bash
pip install --upgrade pip
pip install -r requirements.txt
```


### Levantar el servidor
```bash
export ENVIRONMENT="production"
export PYTHONPATH="/path/to/this/project/
uvicorn main:app --reload
```

Tambien puede usar el script `run_server.sh` que automatiza todos estos pasos y ademas se puede especificar la variable de entorno con la llave `-e` y tambien si quiere eliminar la base de datos luego de apagar el servidor con `--no-persitence`. De todas formas, con la llave `-h` puede ver todas las opciones.

Los valores posibles de ENVIRONMENT son `production`, `test` y `development`. Para cada valor, se crea una base de datos distinta


### Testing

- Se puede usar el Makefile para correr los tests. Pero antes, recordar hacer:
```bash
export PYTHONPATH="/path/to/this/project/
```

- Para correr los unittests:
```bash
make run_unit_tests
```

- Para correr los integration tests:
```bash
make run_integration_tests
```

- Para correr todos los tests y ver el coverage total
```bash
make run_coverage
open htmlcov/index.html &
```

Para abrir el archivo desde la consola se puede usar `open` en algunas distribuciones de linux, sino tambien se puede usar el comando `firefox`
para abrirlo si es que tiene firefox instalado. En caso de no poder abrirlo a la consola, puede ir, dentro del proyecto, a ./htmlcov/ y clickear el archivo index.htlm y eso deberia abrirle una pestania en su navegador predeterminado con el reporte del coverage.