## Importador de csv para ppunr
Importador de csv/excel con ideas de ppunr a base de datos mongo 3.2

Probado con python 3.8.3

### Para usar este script
Generar el dump con   
`python3 importador-escuelas.py ARCHIVO.csv`

Importar a mongo local con    
`mongo localhost:27017/ppunre-prod dump-NUMERO.js`   
_(imprime `FIN!` si anda bien)_

### Para restorear una base de datos de producción a entorno local
Descargar el backup .gz del servidor

Descomprimir el backup (con `gunzip`) extrayendo así un archivo `mongo32-NUMERO`

Crear container de prueba con   
`docker run -p 27017:27017 --name mongodb-azure -d mongo:3.2`

Importar backup con   
`mongorestore -h localhost:27017 -d ppunre-prod --archive=mongo32-NUMERO`

Editar en `config/development.json` el parámetro de conexión   
`"mongoUrl": "mongodb://localhost:27017/ppunre-prod"`

### Para facultades cambiar `ppunre-prod` por `ppunr-prod` y usar el script `importador-facultades.py`
