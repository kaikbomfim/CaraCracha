import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "<cole aqui>"
})

ref = db.reference('Students')

data = {
    "3328531":
        {
            "id": "3328531",
            "name": "Kaik Bomfim",
            "password": "102030Kaik",
            "birthdate": "2003-01-07",
            "address": "Vitória da Conquista, Bahia",
            "email": "kaikbomfim@gmail.com",
            "major": "Computacao",
            "starting_year": 2021,
            "standing": "B",
            "total_attendance": 16,
            "year": 3,
            "last_attendance_time": "2024-04-30 22:13:55",
            "content": "Esta seção tem como objetivo oferecer orientações essenciais para que os alunos concluam o curso com êxito. Será atualizado regularmente \
                 para garantir a sua relevância e utilidade. Fique ligado em valiosos \
                 insights e dicas que ajudarão você a se destacar em seus estudos."
        },
    "1826147":
        {
            "id": "1826147",
            "name": "Alessandra Negrini",
            "password": "102030Alessandra",
            "birthdate": "1970-08-29",
            "address": "São Paulo, São Paulo",
            "email": "alessandranegrini@gmail.com",
            "major": "Artes",
            "starting_year": 2022,
            "standing": "R",
            "total_attendance": 7,
            "year": 2,
            "last_attendance_time": "2024-04-30 22:21:27",
            "content": "Esta seção tem como objetivo oferecer orientações essenciais para que os alunos concluam o curso com êxito. Será atualizado regularmente \
                 para garantir a sua relevância e utilidade. Fique ligado em valiosos \
                 insights e dicas que ajudarão você a se destacar em seus estudos."
        },
    "1517262":
        {
            "id": "1517262",
            "name": "Elon Musk",
            "password": "102030Elon",
            "birthdate": "1971-06-28",
            "address": "Boca Chica, Texas",
            "email": "elonmusk@gmail.com",
            "major": "Eletrica",
            "starting_year": 2021,
            "standing": "M",
            "total_attendance": 8,
            "year": 3,
            "last_attendance_time": "2024-04-30 22:25:08",
            "content": "Esta seção tem como objetivo oferecer orientações essenciais para que os alunos concluam o curso com êxito. Será atualizado regularmente \
                 para garantir a sua relevância e utilidade. Fique ligado em valiosos \
                 insights e dicas que ajudarão você a se destacar em seus estudos."
        },
    "1453231":
        {
            "id": "1453231",
            "name": "Bruno Braga",
            "password": "102030Bruno",
            "birthdate": "2002-11-25",
            "address": "Ilhéus, Bahia",
            "email": "brunobraga@gmail.com",
            "major": "Eng. Producao",
            "starting_year": 2021,
            "standing": "B",
            "total_attendance": 5,
            "year": 3,
            "last_attendance_time": "2024-05-02 17:40:08",
            "content": "Esta seção tem como objetivo oferecer orientações essenciais para que os alunos concluam o curso com êxito. Será atualizado regularmente \
                 para garantir a sua relevância e utilidade. Fique ligado em valiosos \
                 insights e dicas que ajudarão você a se destacar em seus estudos."
        }
}

for key, value in data.items():
    ref.child(key).set(value)