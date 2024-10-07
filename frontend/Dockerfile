# Dockerfile para o frontend
FROM node:18 AS build

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos do projeto
COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Construindo a aplicação Angular
RUN npm run build --prod

# Servindo a aplicação usando o Nginx
FROM nginx:alpine
COPY --from=build /app/dist/youtube-downloader/browser /usr/share/nginx/html/

# Expondo a porta do Nginx
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
