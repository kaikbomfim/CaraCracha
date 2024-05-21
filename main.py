from flask import Flask, render_template, Response, redirect, url_for, request
import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, storage, db
from datetime import datetime
import json

app = Flask(__name__) # Inicializando flask

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "<cole aqui>",
    'storageBucket': "<cole aqui>"
})

bucket = storage.bucket()

def dataset(id):
    # Resgata as informações do aluno uma única vez do banco de dados
    studentInfo = db.reference(f'Students/{id}').get()
    # Resgata a imagem do armazenamento
    blob = bucket.get_blob(f"static/Files/Images/{id}.png")
    array = np.frombuffer(blob.download_as_string(), np.uint8)
    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
    # Atualiza valor da frequência
    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
    return studentInfo, imgStudent, secondsElapsed

already_marked_id_student = []
already_marked_id_admin = []

def generate_frame():
    # Importação da câmera e definição de dimensões da tela
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # Largura
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # Altura

    # imgBackground = cv2.imread('static/Files/Resources/background.png')
    imgBackground = cv2.imread('static/Files/Resources/background.png')

    # Importando os modelos de imagem para uma lista
    folderModePath = 'static/Files/Resources/Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = []
    for path in modePathList:
        imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
    
    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    # Carrega o arquivo de codificações
    file = open("EncodeFile.p", 'rb')
    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown, studentIds = encodeListKnownWithIds

    while True:
        # Leitura do streaming da webcam
        success, img = cap.read()

        if not success:
            break
        else:
            # Redefine a dimensão da imagem para um menor tamanho
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Identifica a posição da face no frame atual (webcam)
            faceCurFrame = face_recognition.face_locations(imgS)
            # Codifica a face encontrada
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            # Define as dimensões para dispor a webcam no background
            imgBackground[162:162 + 480, 55:55 + 640] = img
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    # Compara o frame capturado com as faces conhecidas (já armazenadas)
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    """
                    Fornece uma distância numérica para comparar a similaridade
                    entre as faces conhecidas e a face atual (frame). 
                    Quanto menor a distância, maior a similaridade.
                    """
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    
                    if matches[matchIndex]:
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                        id = studentIds[matchIndex]
                        if counter == 0:
                            cvzone.putTextRect(imgBackground, "Carregando", (65, 200), thickness=2)
                            cv2.waitKey(1)
                            counter = 1
                            modeType = 1
                    else:
                        cvzone.putTextRect(imgBackground, "Carregando", (65, 200), thickness=2)
                        cv2.waitKey(3)
                        cvzone.putTextRect(imgBackground, "Face nao encontrada", (65, 200), thickness=2)
                        modeType = 4
                        counter = 0
                        imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
                            modeType
                        ]

                if counter != 0:
                    if counter == 1:
                        # Resgata as informações do aluno uma única vez do banco de dados
                        studentInfo, imgStudent, secondsElapsed = dataset(id)
                        # Adiciona uma nova frequência, caso a última tenha sido
                        # superior a 24 horas
                        if secondsElapsed > 10:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            modeType = 3
                            counter = 0
                            imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]

                            already_marked_id_student.append(id)
                            already_marked_id_admin.append(id)
                            
                    if modeType != 3:
                        if 5 < counter < 10:
                            modeType = 2
                        
                        imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]

                        if counter <= 5:
                            # Aloca as informações na tela
                            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                            # Ajustes para centralizar o nome do estudante 
                            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                            offset = (414 - w) // 2
                            cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                            imgBackground[175: 175 + 216, 909: 909 + 216] = imgStudent
                    
                        counter += 1

                        if counter >= 10:
                            counter = 0
                            modeType = 0
                            studentInfo = []
                            imgStudent = []
                            imgBackground[44:44 + 633, 808: 808 + 414] = imgModeList[modeType]
            else:
                modeType = 0
                counter = 0    

            ret, buffer = cv2.imencode(".jpeg", imgBackground)
            frame = buffer.tobytes()

        yield (b"--frame\r\n" b"Content-Type: image/jpeg \r\n\r\n" + frame + b"\r\n")

def add_image_database():
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
    
    return studentIds, imgList

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

    # Criando a tela de streaming da câmera 
    # cv2.imshow("CaraCracha", imgBackground)
    # cv2.waitKey(1)

### ROTAS ###

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    return Response(
        generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    id = request.form.get("id_number", False)
    email = request.form.get("email", False)
    password = request.form.get("password", False)
    studentIds, _ = add_image_database()

    if id:
        if id not in studentIds:
            return render_template(
                "student_login.html", data=" ❌ A matrícula não está registrada"
            )
        else:
            secret_key = f"{id}{email}{password}whubaxj"
            hash_secret_key = str(hash(secret_key))
            if(
                dataset(id)[0]["password"] == password
                and dataset(id)[0]["email"] == email
            ):
                return redirect(url_for("student", data=id, title=hash_secret_key))
            else:
                id = False
                return render_template(
                    "student_login.html", data=" ❌ Email/Senha Incorretos"
                )
    else:
        return render_template("student_login.html")

@app.route("/student/<data>/<title>")
def student(data, title=None):
    studentInfo, imgStudent, secondsElapsed = dataset(data)
    hoursElapsed = round((secondsElapsed / 3600), 2)

    info = {
        "studentInfo": studentInfo,
        "lastLogin": hoursElapsed,
        "image": imgStudent,
    }

    return render_template("student.html", data=info)

@app.route("/student_attendance_list")
def student_attendance_list():
    unique_id_student = list(set(already_marked_id_student))
    student_info = []
    for i in unique_id_student:
        student_info.append(dataset(i))
    return render_template("student_attendance_list.html", data=student_info)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    id = request.form.get("id_number", False)
    email = request.form.get("email", False)
    password = request.form.get("password", False)
    studentIds, _ = add_image_database()

    if id:
        if id not in studentIds:
            return render_template(
                "admin_login.html", data =" ❌ A matrícula não está registrada"
            )
        else:
            if(
                dataset(id)[0]["password"] == password
                and dataset(id)[0]["email"] == email
            ):
                return redirect(url_for("admin"))
            else:
                id = False
                return render_template(
                    "admin_login.html", data=" ❌ Email/Senha Incorretos "
                )
    else:
        return render_template("admin_login.html")        

@app.route("/admin")
def admin():
    all_student_info = []
    studentIds, _ = add_image_database()
    for i in studentIds:
        all_student_info.append(dataset(i))
    return render_template("admin.html", data=all_student_info)

@app.route("/admin/admin_attendance_list", methods=["GET", "POST"])
def admin_attendance_list():
    if request.method == "POST":
        if request.form.get("button_student") == "VALUE1":
            already_marked_id_student.clear()
            return redirect(url_for("admin_attendance_list"))
        else:
            request.form.get("button_admin") == "VALUE2"
            already_marked_id_admin.clear()
            return redirect(url_for("admin_attendance_list"))
    else:
        unique_id_admin = list(set(already_marked_id_admin))
        student_info = []
        for i in unique_id_admin:
            student_info.append(dataset(i))
        return render_template("admin_attendance_list.html", data=student_info)

@app.route("/admin/add_user", methods=["GET", "POST"])
def add_user():
    id = request.form.get("id", False)
    name = request.form.get("name", False)
    password = request.form.get("password", False)
    birthdate = request.form.get("birthdate", False)
    city = request.form.get("city", False)
    country = request.form.get("country", False)
    phone = request.form.get("phone", False)
    email = request.form.get("email", False)
    major = request.form.get("major", False)
    starting_year = request.form.get("starting_year", False)
    standing = request.form.get("standing", False)
    total_attendance = request.form.get("total_attendance", False)
    year = request.form.get("year", False)
    last_attendance_date = request.form.get("last_attendance_date", False)
    last_attendance_time = request.form.get("last_attendance_time", False)
    content = request.form.get("content", False)

    address = f"{city}, {country}"
    last_attendance_datetime = f"{last_attendance_date} {last_attendance_time}:00"
    year = int(year)
    total_attendance = int(total_attendance)
    starting_year = int(starting_year)

    if request.method == "POST":
        image = request.files["image"]
        filename = f"{'static/Files/Images'}/{id}.png"
        image.save(os.path.join(filename))
    
    studentIds, imgList = add_image_database()

    encodeListKnown = findEncodings(imgList)
    
    encodeListKnownWithIds = [encodeListKnown, studentIds]
    """
    Cria um arquivo e adiciona a lista de codificação das imagens
    com seus respectivos IDs
    """
    file = open("EncodeFile.p", 'wb')
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

    if id:
        add_student = db.reference(f"Students")

        add_student.child(id).set(
            {
                "id": id,
                "name": name,
                "password": password,
                "birthdate": birthdate,
                "address": address,
                "phone": phone,
                "email": email,
                "major": major,
                "starting_year": starting_year,
                "standing": standing,
                "total_attendance": total_attendance,
                "year": year,
                "last_attendance_time": last_attendance_datetime,
                "content": content,
            }
        )
    
    return render_template("add_user.html")

@app.route("/admin/edit_user", methods=["POST", "GET"])
def edit_user():
    value = request.form.get("edit_student")

    studentInfo, imgStudent, secondsElapsed = dataset(value)
    hoursElapsed = round((secondsElapsed / 3600), 2)

    info = {
        "studentInfo": studentInfo,
        "lastLogin": hoursElapsed,
        "image": imgStudent,
    }

    return render_template("edit_user.html", data=info)

@app.route("/admin/save_changes", methods=["POST", "GET"])
def save_changes():
    content = request.get_data()

    dic_data = json.loads(content.decode("utf-8"))

    dic_data = {k: v.strip() for k, v in dic_data.items()}

    dic_data["year"] = int(dic_data["year"])
    dic_data["total_attendance"] = int(dic_data["total_attendance"])
    dic_data["starting_year"] = int(dic_data["starting_year"])

    update_student = db.reference(f"Students")

    update_student.child(dic_data["id"]).update(
        {
            "id": dic_data["id"],
            "name": dic_data["name"],
            "birthdate": dic_data["birthdate"],
            "address": dic_data["address"],
            "phone": dic_data["phone"],
            "email": dic_data["email"],
            "major": dic_data["major"],
            "starting_year": dic_data["starting_year"],
            "standing": dic_data["standing"],
            "total_attendance": dic_data["total_attendance"],
            "year": dic_data["year"],
            "last_attendance_time": dic_data["last_attendance_time"],
            "content": dic_data["content"], 
        }
    )

    return "Dados recebidos com sucesso!"

def delete_image(student_id):
    filepath = f"static/Files/Images/{student_id}.png"

    os.remove(filepath)

    bucket = storage.bucket()
    blob = bucket.blob(filepath)
    blob.delete()

    return "Sucesso!"

@app.route("/admin/delete_user", methods=["POST", "GET"])
def delete_user():
    content = request.get_data()

    student_id = json.loads(content.decode("utf-8"))

    delete_student = db.reference(f"Students")
    delete_student.child(student_id).delete()

    delete_image(student_id)

    studentIds, imgList = add_image_database()

    encodeListKnown = findEncodings(imgList)

    encodeListKnownWithIds = [encodeListKnown, studentIds]

    file = open("EncodeFile.p", "wb")
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

    return "Sucesso!"

if __name__ == "__main__":
    app.run(debug=True)