from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import threading
import hashlib  # Adicionar biblioteca para gerar hash MD5


app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = 'downloads'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Dicionário para armazenar threads de download e seus status de controle
download_threads = {}
download_control = {}

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
def download():
    data = request.json
    link = data.get('link')

    if not link:
        return jsonify({'error': 'Nenhum link fornecido'}), 400

    # Gerar um thread_id seguro (hash MD5 do link)
    thread_id = generate_thread_id(link)
    
    try:
        # Iniciar o download em uma thread separada
        thread = threading.Thread(target=baixar_youtube_mp3, args=(link, thread_id))
        thread.start()
        download_threads[thread_id] = thread
        download_control[thread_id] = 'running'
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
def list_mp3_files():
    try:
        # Obtém a lista de arquivos da pasta
        files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.mp3')]
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para baixar o arquivo
@app.route('/download/<filename>', methods=['GET'])
def get_file(filename):
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)  # Força o download
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
