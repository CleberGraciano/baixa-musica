# Dockerfile

# Use a imagem do Python como base
FROM python:3.9-slim

# Atualize a lista de pacotes e instale FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Defina o diretório de trabalho
WORKDIR /app

# Crie o diretório data e ajuste as permissões
RUN mkdir -p data && chmod -R 775 data

# Copie os arquivos de requisitos e instale as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código
COPY . .

# Comando para rodar a aplicação
CMD ["flask", "run", "--host=0.0.0.0"]
