<div align="center">
    <a href="https://github.com/kaikbomfim" target="_blank">
        <img src="https://github.com/kaikbomfim/CaraCracha/blob/main/misc/app.png" 
        alt="Logo" width="800" height="350">
    </a>
</div>

<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=50&duration=3000&pause=200&color=7ED957&center=true&vCenter=true&multiline=true&random=false&width=435&height=100&lines=CaraCrach%C3%A1">
</div>

<h2 align="center">Registre a frequência dos alunos atráves de um sistema de reconhecimento facial</h2>

## Descrição

O CaraCrachá é uma aplicação web feita em Python que integra ferramentas como Flask, Firebase (banco de dados) e as bibliotecas FaceRecognition e OpenCV
para emular um sistema de registro de frequência escolar dos estudantes por meio do reconhecimento facial.

Confira o vídeo de demonstração da aplicação clicando [aqui]().

## Configurações

- Para utilizar a aplicação, faça a cópia do repositório para a sua máquina local. Em seu terminal, use o seguinte comando:

```bash
    git clone https://github.com/kaikbomfim/CaraCracha.git
```

- Em seguida, instale todos os módulos listados no arquivo **requirements.txt**, usando o comando abaixo:

```python
    pip install -r requirements.txt
```

- Prossiga com as configurações do seu banco de dados Firebase. Baixe as credenciais necessárias do Firebase e salve-as como **serviceAccountKey.json**.
- Localize o arquivo **AddDataToDatabase.py** na pasta **misc**. Abra-o e encontre a seção para colar a URL do seu banco de dados. Se sua configuração e credenciais estiverem corretas, o script adicionará os dados ao banco de dados.
- Depois de criar o banco de dados, execute o arquivo **EncodeGenerator.py**. Certifique-se de que as imagens dos usuários foram salvas em **static/Files/Images** e nomeadas com o respectivo ID do usuário. Além disso, essa etapa também irá gerar um arquivo pickle usado para o modelo de reconhecimento facial.
- Concluídas as etapas anteriores, execute o arquivo **main.py**. Se todas as credenciais e dependências estiverem configuradas corretamente, o aplicativo web deverá começar a ser executado.

## Referências

- [Face Recognition with Real-Time Database | 2 Hour Course | Computer Vision](https://www.youtube.com/watch?v=iBomaK2ARyI)
- [Face-Recognition-System-for-Student-Attendance](https://github.com/itsmeSamrat/Face-Recognition-System-for-Student-Attendance)
