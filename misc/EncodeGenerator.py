import cv2, os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "<cole aqui>",
    'storageBucket': "<cole aqui>"
})

# Importando as imagens dos estudantes
folderPath = 'static/Files/Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in pathList:
    # Adiciona as imagens dos estudantes em uma lista
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    
    """
    Adiciona os nomes das imagens (IDs) em uma lista
    Obs.: splitext recupera apenas o primeiro termo e desconsidera
    o segundo termo (Ex.: 3328531.png = ['3328531', 'png'])
    """ 
    studentIds.append(os.path.splitext(path)[0])

    # Upload das imagens para o Google Cloud Storage via FireBase
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # Converte a imagem do padrão de cores do OpenCV
        # para o do FaceRecognition
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Encontra e armazena as codificações faciais da imagem
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList

print("Codificação iniciada ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Codificação concluída")

"""
Cria um arquivo e adiciona a lista de codificação das imagens
com seus respectivos IDs
"""
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("Arquivo salvo")

