import json
import urllib
import time

from flask import Flask, request
from flask_cors import CORS, cross_origin
import boto3
import psycopg2
import requests

app = Flask(__name__)
CORS(app)
bucketName = "credencialesinside"
itemname = "credentials.json"



def auth():
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(bucketName, itemname)
        body = obj.get()['Body'].read()
        json_content = json.loads(body)

        return json_content
    except:
        return False

def connect():
    json_str = json.dumps(auth())
    resp = json.loads(json_str)

    user = resp['desarrollo']['usuariobasededatos']
    password = resp['desarrollo']['passwordbasededatos']
    dbname = resp['desarrollo']['dbname']
    host = resp['desarrollo']['host']

    if resp != False:
        pass

    else:
        salida = False
        return salida, 401

    try:
        conn = psycopg2.connect(
            "dbname='" + dbname + "' user='" + user + "'host='" + host + "' password='" + password + "'")

        return conn

    except Exception as e:
        print(str(e))
        exit()

        return False

    except Exception as e:
        print(str(e))
        return False
        exit()


def getEmailFromID(id):
    con = connect()
    cur = con.cursor()
    print("id a consultar email: "+id)
    try:
        cur.execute("select email from user_ where id = " + id + " and elimination IS NULL""")
        result = cur.fetchone()
        print(result[0])
        print("El email ha sido encontrado")
        return result[0]

    except Exception as e:
        print("Error de consulta de email")
        print(str(e))
        cur.close()
        con.close()
        return 0
        exit()
def check_collection(collectionName):
    max_results = 2
    resultado = 0

    client = boto3.client('rekognition','us-east-1')

    # Display all the collections
    print('Displaying collections...')
    response = client.list_collections(MaxResults=max_results)
    done = False

    while done == False:
        collections = response['CollectionIds']

        for collection in collections:
            print(collection)
            if(collection == collectionName):
                resultado = 1
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = client.list_collections(NextToken=nextToken, MaxResults=max_results)

        else:
            done = True

        return resultado

app = Flask(__name__)

# here is how we are handling routing with flask:
def list_collections():
    max_results = 2

    client = boto3.client('rekognition')

    # Display all the collections
    print('Displaying collections...')
    response = client.list_collections(MaxResults=max_results)
    collection_count = 0
    done = False

    listCollection = []
    collections = response['CollectionIds']
    listFaces = []
    response = client.list_collections(MaxResults=300)
    for collection in collections:
        print(collection)
        response2 = client.list_faces(CollectionId=collection, MaxResults=300)
        faces = response2['Faces']
        for face in faces:
            print(face)
            listFaces.append(face)
        #print(response2['ExternalImageId'])
        collection_count += 1
    listCollection.append(listFaces)

    return listCollection

@app.route('/limpiarCollection', methods=["POST"])
@cross_origin(supports_credentials=True)
def limpiarCollection():
    jsonResponse = {}
    collection_id = "MyCollection"
    print("entramos a limpiar collection faces: ")
    maxResults = 2
    faces_count = 0
    tokens = True

    client = boto3.client('rekognition')
    response = client.list_faces(CollectionId=collection_id,
                                 MaxResults=maxResults)

    print('Faces in collection ' + collection_id)

    while tokens:

        faces = response['Faces']

        for face in faces:
            print(face)
            faces = []
            faces.append(face["FaceId"])
            response2 = client.delete_faces(CollectionId=collection_id,
                                           FaceIds=faces)

            print(str(len(response2['DeletedFaces'])) + ' faces deleted:')
            for faceId in response2['DeletedFaces']:
                print(faceId)
            faces_count += 1
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = client.list_faces(CollectionId=collection_id,
                                         NextToken=nextToken, MaxResults=maxResults)
        else:
            tokens = False
    return faces_count


@app.route('/listarFaces', methods=["POST"])
@cross_origin(supports_credentials=True)
def listarFaces():
    jsonResponse = {}
    print("entramos a listar faces: ")
    max_results = 2

    client = boto3.client('rekognition')

    # Display all the collections
    print('Displaying collections...')
    response = client.list_collections(MaxResults=max_results)
    collection_count = 0
    done = False
    tokens = True

    while done == False:
        collections = response['CollectionIds']
        faces_count = 0
        for collection in collections:
            print("HHH"+collection)
            collection_count += 1
            client = boto3.client('rekognition')
            response = client.list_faces(CollectionId=collection,
                                         MaxResults=2)

            print('Faces in collection ' + collection)

            while tokens:

                faces = response['Faces']

                for face in faces:
                    print("HHHHH"+face["ExternalImageId"])
                    faces_count += 1
                if 'NextToken' in response:
                    nextToken = response['NextToken']
                    response = client.list_faces(CollectionId=collection, NextToken=nextToken, MaxResults=2)
                else:
                    tokens = False
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = client.list_collections(NextToken=nextToken, MaxResults=max_results)

        else:
            done = True

    return jsonResponse, 200
@app.route('/verificarUsuario', methods=["POST"])
@cross_origin(supports_credentials=True)
def verificarUsuario():
    jsonResponse = {}
    jsonResponse["respuesta"] = False
    print(request.args['nombreImagen'])

    # Validaciones

    if request.json is None:
        jsonResponse["respuesta"] = False
        jsonResponse["error"] = "No se envio body en la solicitud"
        return jsonResponse, 400
    else:
        content = request.json
        pass
    print("JSON de entrada:" + str(content))
    if request.args['nombreImagen'] is not None:
        pass
    else:
        jsonResponse["respuesta"] = False
        jsonResponse["error"] = "nombreImagen es obligatorio"
        return jsonResponse, 500

   # if request.args['email'] is not None:
    #    pass
    #else:
    #    jsonResponse["respuesta"] = False
    #    jsonResponse["error"] = "email es obligatorio"
    #    return jsonResponse, 500

    # replace bucket, collectionId, and photo with your values.
    nombreImagen = str(request.args['nombreImagen'])
    #email = str(request.args['email'])
    print("nombreImagen: "+nombreImagen)
   # print("email: "+email)
    #if(idUsuario == 0):
    #No se encontro el ID
     #   jsonResponse["error"] = 'No se pudo encontrar el id del usuario'
      #  jsonResponse["respuesta"] = False
       # return jsonResponse, 500

    collectionId = "MyCollection"
    client = boto3.client('rekognition','us-east-1')
    s3 = boto3.resource('s3','us-east-1')
    # Revisamos que la collection no exista y si no existe la creamos
    #if (check_collection(collectionId) == 0):
    #    print("Entramos al collection")
    #    print("Collection no encontrada, procedemos a crearla")
        # Create a collection
    #    print('Creating collection:' + collectionId)
    #    response = client.create_collection(CollectionId=collectionId)

     #   print('Collection ARN: ' + response['CollectionArn'])
     #   print('Status code: ' + str(response['StatusCode']))
     #   print('Done...')

    bucket = 'recognitionprueba'
    myBucket = s3.Bucket(bucket)
    threshold = 70
    maxFaces = 2
    # indexamos la imagen

    jsonResponse["error"] = "No se pudo comparar la imagen, imagen no encontrada"
    for myBucketObject in myBucket.objects.all():
        if nombreImagen == myBucketObject.key:
            try:
                response = client.search_faces_by_image(CollectionId=collectionId,
                                                        Image={
                                                            'S3Object': {'Bucket': bucket, 'Name': myBucketObject.key}},
                                                        FaceMatchThreshold=threshold,
                                                        MaxFaces=maxFaces)
            except Exception as e:
                if "There are no faces in the image. Should be at least 1." in str(e):
                    #no se encontraron rostros en la imagen
                    jsonResponse["respuesta"] = False
                    jsonResponse["error"] = "NoFacesFound"
                    print(e)
                    return jsonResponse,500
            jsonResponse["error"] = "Usuario no encontrado"
            faceMatches = response['FaceMatches']
            print('response')
            print(response)
            print('Matching faces')
            for match in faceMatches:
                #Verificamos el ID del usuario
                print('IMAGEID: '+match['Face']['ExternalImageId'])
               # if match['Face']['ExternalImageId'] == str(idUsuario):
                    #Encontramos el usuario
                print('FaceId:' + match['Face']['FaceId'])
                print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                print("Done...")

                email = getEmailFromID(match['Face']['ExternalImageId'])
                jsonResponse["email"] = email
                jsonResponse["idUsuario"] = match['Face']['ExternalImageId']
                jsonResponse["respuesta"] = True
                jsonResponse["error"] = ''
                return jsonResponse, 200

    jsonResponse["respuesta"] = False
    return jsonResponse, 500

@app.route('/borrarImagen', methods=["POST"])
@cross_origin(supports_credentials=True)
def deleteImageFromID():
    print("entramos a borrar imagen: ID="+request.args['idImagen'])
    collectionId = "MyCollection"
    client = boto3.client('rekognition', 'us-east-1')
    s3 = boto3.resource('s3', 'us-east-1')
    bucket = 'recognitionprueba'
    jsonResponse = {}
    jsonResponse["respuesta"] = False
    myBucket = s3.Bucket(bucket)
    print("Entramos a listFacesInCollection: ");
    maxResults = 2
    tokens = True
    # Display all the collections
    response = client.list_faces(CollectionId=collectionId,
                                 MaxResults=maxResults)

    print('Faces in collection ' + collectionId)

    while tokens:

        faces = response['Faces']

        for face in faces:
            print(face)
            if face['ExternalImageId'] == request.args['idImagen']:
                faceList = []
                faceList.append(face['FaceId'])
                response = client.delete_faces(CollectionId=collectionId,
                                               FaceIds=faceList)

                print(str(len(response['DeletedFaces'])) + ' faces deleted:')
                for faceId in response['DeletedFaces']:
                    print(faceId)
                jsonResponse["respuesta"]=True
                jsonResponse["error"] = ""
                return jsonResponse,200
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = client.list_faces(CollectionId=collectionId,
                                         NextToken=nextToken, MaxResults=maxResults)
        else:
            tokens = False

    jsonResponse["respuesta"] = False
    jsonResponse["error"] = "No se pudo indexar la imagen, imagen no encontrada"
    return jsonResponse, 500

@app.route('/updateImageId', methods=["POST"])
@cross_origin(supports_credentials=True)
def updateImageId():
    print("entramos a actualizar el id de la imagen: IDActual="+request.args['idActual']+" IDNuevo="+request.args['idNuevo']+" - "+request.args["imageName"])
    #time.sleep(3)
    collectionId = "MyCollection"
    nombreImagen = request.args["imageName"]
    idUsuario = request.args["idNuevo"]
    idActual = request.args['idActual']
    client = boto3.client('rekognition', 'us-east-1')
    s3 = boto3.resource('s3', 'us-east-1')
    bucket = 'recognitionprueba'
    myBucket = s3.Bucket(bucket)
    jsonResponse = {}
    jsonResponse["respuesta"] = False
    print("Entramos a listFacesInCollection: ");
    maxResults = 2
    tokens = True
    # Display all the collections
    response = client.list_faces(CollectionId=collectionId,
                                 MaxResults=maxResults)

    print('Faces in collection ' + collectionId)

    faces = response['Faces']
    print("Imprimimos como esta")
    for face in faces:
        print(face["ExternalImageId"])

    print("Terminamos de imprimir el collection")
    while tokens:

        for face in faces:
            print(face)
            print(face['ExternalImageId']+" - "+request.args['idActual'])
            if face['ExternalImageId'] == request.args['idActual']:
                print("Encontramos la imagen a actualizar")
                faceList = []
                faceList.append(face['FaceId'])
                response = client.delete_faces(CollectionId=collectionId, FaceIds=faceList)
                print(str(len(response['DeletedFaces'])) + ' faces deleted:')
                for faceId in response['DeletedFaces']:
                    print(faceId)
                print("Imagen presuntamente borrada")
                print(face)
                for myBucketObject in myBucket.objects.all():
                    print("Buscamos la imagen de nuevo en el bucket")
                    print(nombreImagen+" - "+myBucketObject.key)
                    if nombreImagen == myBucketObject.key:
                        print("Encontramos la imagen deseada, vamos a indexarla")
                        response = client.index_faces(CollectionId=collectionId,
                                                      Image={
                                                          'S3Object': {'Bucket': bucket, 'Name': myBucketObject.key}},
                                                      ExternalImageId=idUsuario,
                                                      MaxFaces=1,
                                                      QualityFilter="AUTO",
                                                      DetectionAttributes=['ALL'])

                        print('Results for ' + myBucketObject.key)
                        print('Faces indexed:')
                        for faceRecord in response['FaceRecords']:
                            print('  Face ID: ' + faceRecord['Face']['FaceId'])
                            print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
                            try:
                                print("Intentamos copiar la imagen")
                                s3.Object(bucket, "aidicareindexados/" + myBucketObject.key).copy_from(
                                    CopySource=urllib.parse.quote(bucket + "/" + myBucketObject.key))
                                print("Imagen Copiada")
                            except:
                                print("Error copiando: ")
                                jsonResponse["respuesta"] = False
                                return jsonResponse, 500
                            try:
                                print("intentamos borrar la imagen")
                                s3.Object(bucket, myBucketObject.key).delete()
                                print("Imagen Borrada")
                            except:
                                print("Error borrando")
                                jsonResponse["respuesta"] = False
                                return jsonResponse, 500
                            jsonResponse["respuesta"] = True
                            return jsonResponse, 200

                        print('Faces not indexed:')
                        for unindexedFace in response['UnindexedFaces']:
                            print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
                            print(' Reasons:')
                            for reason in unindexedFace['Reasons']:
                                print('   ' + reason)

                print(face)
                jsonResponse["respuesta"] = True
                jsonResponse["error"] = ""
                return jsonResponse, 200
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = client.list_faces(CollectionId=collectionId,
                                         NextToken=nextToken, MaxResults=maxResults)
        else:
            tokens = False



    jsonResponse["respuesta"] = False
    jsonResponse["error"] = "No se pudo indexar la imagen, imagen no encontrada"
    return jsonResponse, 500

@app.route('/indexar', methods=["POST"])
@cross_origin(supports_credentials=True)
def indexar():

    collectionId = "MyCollection"
    client = boto3.client('rekognition','us-east-1')
    s3 = boto3.resource('s3','us-east-1')
    jsonResponse = {}
    jsonResponse["respuesta"] = False
    print(request.args['nombreImagen'])

    # Validaciones

    if request.json is None:
        jsonResponse["respuesta"] = False
        jsonResponse["error"] = "No se envio body en la solicitud"
        return jsonResponse, 400
    else:
        content = request.json
        pass
    print("JSON de entrada:" + str(content))
    if request.args['nombreImagen'] is not None:
        pass
    else:
        jsonResponse["respuesta"] = False
        jsonResponse["error"] = "nombreImagen es obligatorio"
        return jsonResponse, 500

    if request.args['idUsuario'] is not None:
        pass
    else:
        jsonResponse["respuesta"] = False
        jsonResponse["error"] = "idUsuario es obligatorio"
        return jsonResponse, 500

    nombreImagen = request.args['nombreImagen']
    idUsuario = request.args['idUsuario']
    print("nombreImagen: " + nombreImagen)
    print("idUsuario: " + idUsuario)



    bucket = 'recognitionprueba'
    myBucket = s3.Bucket(bucket)
    # indexamos la imagen
    for myBucketObject in myBucket.objects.all():
        if nombreImagen == myBucketObject.key:
            response = client.index_faces(CollectionId=collectionId,
                                          Image={'S3Object': {'Bucket': bucket, 'Name': myBucketObject.key}},
                                          ExternalImageId=idUsuario,
                                          MaxFaces=1,
                                          QualityFilter="AUTO",
                                          DetectionAttributes=['ALL'])
            print(response)
            print('Results for ' + myBucketObject.key)
            print('Faces indexed:')
            for faceRecord in response['FaceRecords']:
                print('  Face ID: ' + faceRecord['Face']['FaceId'])
                print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
                jsonResponse["respuesta"] = True
                return jsonResponse, 200
            # Movemos la imagen a la carpeta de indexados
    jsonResponse["respuesta"] = False
    jsonResponse["error"] = "No se pudo indexar la imagen, imagen no encontrada o rostro no identificado"
    return jsonResponse, 500
# include this for local dev

if __name__ == '__main__':
    app.run()
