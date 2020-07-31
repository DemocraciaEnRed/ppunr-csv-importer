'''
== Para restorear una base de datos de producción
Descargar y descomprimir del backup .gz el archivo mongo32-NUMERO (con gunzip)
$ docker run -p 27017:27017 --name mongodb-azure -d mongo:3.2
$ mongorestore -h localhost:27017 -d ppunre-prod --archive=mongo32-NUMERO
Editar en config/development.json "mongoUrl": "mongodb://localhost:27017/ppunre-prod"

== Para usar este script
$ python3 importador-escuelas.py ARCHIVO.csv
$ mongo localhost:27017/ppunre-prod dump-NUMERO.json
Imprime FIN! si anda bien
'''

import sys
import csv
import re

if len(sys.argv) < 2:
	print('Debes pasar el nombre del csv como primer parámetro')
	sys.exit(1)	
FNAME=sys.argv[1]

def parsear(archivo):
  data_parseada = {}
  
  COL_COMENT=0
  COL_LINK_ID=1
  COL_TIPO=2
  COL_IDEA_ID=5

  texto_regex = re.compile('^[0-9a-zA-ZáéíóúÁÉÍÓÚñÑü.\'’()!¡?¿:@ -]+$')
  mongo_id_regex = re.compile('^[a-f0-9]{24}$')
  def validar_id(id):
    return mongo_id_regex.match(id)

  def printERR(*msgs):
   print(f'ERROR línea {ROW}:', *msgs)

  ROW=0 
  FATAL=False
  LINEAS_VACIAS=0
  with open(archivo, 'r') as csvfile:
   reader = csv.reader(csvfile)
   next(reader)
   for row in reader:
    ROW+=1
    
    comentario=row[COL_COMENT].strip()
    id_idea_linkeada=row[COL_LINK_ID].strip().lower()
    tipo_idea=row[COL_TIPO].strip().lower()
    id_idea=row[COL_IDEA_ID].strip().lower()
    
    if not id_idea and not comentario:
      LINEAS_VACIAS += 1
      if LINEAS_VACIAS == 2:
        print('Llegado a dos líneas vacías, cortando lectura')
        break
      print(f'Salteando línea {ROW} vacía')
      continue
    LINEAS_VACIAS = 0
    
    if id_idea_linkeada and not validar_id(id_idea_linkeada):
     printERR(f'Mal id linkeado {id_idea_linkeada}')
     FATAL=True
    
    if not validar_id(id_idea):
     printERR(f'Mal id de idea {id_idea}')
     FATAL=True
    
    if not texto_regex.match(comentario):
     printERR(f'Mal comentario "{comentario}"')
     FATAL=True
     
    if tipo_idea not in ['original', 'sistematizada']:
     printERR(f'Mal tipo de idea "{tipo_idea}"')
     FATAL=True
     
    if id_idea in data_parseada:
     printERR(f'Id de idea duplicado "{id_idea}"')
     FATAL=True
     
    if FATAL:
      FATAL=False
      continue
      
    data_parseada[id_idea] = {
      'comentario': comentario,
      'id_idea_linkeada': id_idea_linkeada,
      'tipo_idea': tipo_idea
    }
   #end for    
   print(f'{ROW} líneas procesadas')
  #end with
  return data_parseada

data_parseada = parsear(FNAME)

##### BEGIN DUMP
from datetime import datetime
def tstamp(): return str(int( datetime.now().timestamp() ))

print('Dumping json')
with open(f'dump-{tstamp()}.json', 'w+') as dump_file:
  
  # https://docs.mongodb.com/manual/reference/method/Bulk.find.update/#example
  dump_file.write('var bulk = db.topics.initializeUnorderedBulkOp();\n')
  
  for id_idea, data in data_parseada.items():
    
    comentario = data['comentario']
    id_idea_linkeada = data['id_idea_linkeada']
    tipo_idea = 'pendiente' if data['tipo_idea'] == 'original' else 'sistematizada'
    
    link_idea = f'https://ppescuelas.unr.edu.ar/propuestas/topic/{id_idea_linkeada}' if id_idea_linkeada else ''
    
    query=f'{{ _id: ObjectId("{id_idea}") }}'
    update_params = [
      f'"attrs.admin-comment":"{comentario}"',
      f'"attrs.admin-comment-referencia":"{link_idea}"',
      f'"attrs.state":"{tipo_idea}"'
    ]
    update=f'{{ $set: {{ {", ".join(update_params)} }} }}'
    
    dump_file.write(f'bulk.find({query}).updateOne({update});\n')
    
  #end for
  dump_file.write('bulk.execute();\n')
  dump_file.write('print("FIN!");\n')
  
print('Done!')