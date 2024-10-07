from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import threading
import hashlib  # Adicionar biblioteca para gerar hash MD5
# Adicione essas importações
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt


app = Flask(__name__)
CORS(app, supports_credentials=True)

# Definindo a secret_key
app.secret_key = 'sua_chave_secreta_aqui'  # Substitua por uma chave única e complexa
# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Você pode usar outro banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

# # Defina a rota de redirecionamento em caso de acesso sem login
# login_manager.login_view = 'login'

OUTPUT_FOLDER = 'downloads'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Dicionário para armazenar threads de download e seus status de controle
download_threads = {}
download_control = {}


# Modelo de Usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        # Armazena o hash da senha no banco de dados
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        # Verifica o hash da senha
        return bcrypt.check_password_hash(self.password_hash, password)

# Modelo de Playlist
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    songs = db.relationship('Song', backref='playlist', lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)

# Criar as tabelas no banco de dados
with app.app_context():
    db.create_all()

# Função para carregar um usuário com base no ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Retorna o usuário com o ID fornecido

# Função para gerar um hash MD5 seguro a partir do link
def generate_thread_id(link):
    return hashlib.md5(link.encode()).hexdigest()

# Função para baixar e converter para MP3 com suporte a cancelamento
def baixar_youtube_mp3(link, thread_id, qualidade_kbps=198):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(qualidade_kbps),
            }],
            'outtmpl': os.path.join(OUTPUT_FOLDER, '%(title)s.%(ext)s'),
        }

        def download_progress(d):
            # Verifica se o download foi cancelado
            if download_control.get(thread_id) == 'cancel':
                raise Exception("Download cancelado pelo usuário.")

        ydl_opts['progress_hooks'] = [download_progress]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        download_control.pop(thread_id, None)  # Remove o controle do download ao finalizar
        return os.listdir(OUTPUT_FOLDER)[-1]
    except Exception as e:
        download_control.pop(thread_id, None)
        raise Exception(f"Erro ao baixar: {e}")

# Rota para iniciar o download e permitir o cancelamento
@app.route('/download', methods=['POST'])
@login_required
def download():
    data = request.json
    link = data.get('link')

    if not link:
        return jsonify({'error': 'Nenhum link fornecido'}), 400

    thread_id = generate_thread_id(link)
    
    try:
        thread = threading.Thread(target=baixar_youtube_mp3, args=(link, thread_id))
        thread.start()
        download_threads[thread_id] = thread
        download_control[thread_id] = 'running'
        
        # Adiciona a música à playlist do usuário
        new_song = Song(title=os.path.basename(link), playlist_id=1)  # Crie uma lógica para pegar a playlist correta
        db.session.add(new_song)
        db.session.commit()

        return jsonify({'message': 'Download iniciado', 'thread_id': thread_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para cancelar o download
@app.route('/cancel/<thread_id>', methods=['POST'])
def cancel_download(thread_id):
    try:
        if thread_id in download_control and download_control[thread_id] == 'running':
            download_control[thread_id] = 'cancel'
            return jsonify({'message': 'Download cancelado'}), 200
        else:
            return jsonify({'error': 'Download já finalizado ou não encontrado'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Rota para listar arquivos MP3
@app.route('/list-mp3', methods=['GET'])
@login_required
def list_mp3_files():
    try:
        # Obtém a lista de arquivos da pasta
        files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.mp3')]
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para baixar o arquivo
@app.route('/download/<filename>', methods=['GET'])
@login_required
def get_file(filename):
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)  # Força o download
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Rota de Registro
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Verifica se o usuário já existe
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Usuário já existe.'}), 400

    # Crie uma nova instância do User sem a senha
    new_user = User(username=username)
    
    # Defina a senha com o método set_password
    new_user.set_password(password)

    # Salve o novo usuário no banco de dados
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuário criado com sucesso!'}), 201

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            login_user(user)
            return jsonify({'message': 'Login bem-sucedido!'}), 200
        else:
            return jsonify({'error': 'Nome de usuário ou senha inválidos.'}), 401
    
    # Se for uma requisição GET, pode renderizar uma página de login (HTML)
    return jsonify({'error': 'Use POST para enviar as credenciais.'}), 405

# Rota para criar uma nova playlist
@app.route('/playlists', methods=['POST'])
@login_required
def create_playlist():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'O nome da playlist é obrigatório.'}), 400

    new_playlist = Playlist(name=name, user_id=current_user.id)
    db.session.add(new_playlist)
    db.session.commit()

    return jsonify({'message': 'Playlist criada com sucesso!'}), 201

# Rota de Logout
@app.route('/logout', methods=['POST'])
def logout():
    if not current_user.is_authenticated:
        print("Usuário não está autenticado.")
        return jsonify({'error': 'Não autorizado'}), 401
    logout_user()
    return jsonify({'message': 'Logout bem-sucedido'}), 200


# Rota para listar playlists do usuário logado
@app.route('/playlists', methods=['GET'])
@login_required
def get_playlists():
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    playlists_list = [{'id': playlist.id, 'name': playlist.name} for playlist in playlists]
    return jsonify({'playlists': playlists_list}), 200

    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Isso deve ser executado uma vez para criar as tabelas
    app.run(debug=True)
