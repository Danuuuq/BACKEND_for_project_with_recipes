# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
RUN mkdir -p /static/docs && cp -r build result_build && cp -r docs /static/docs
CMD cp -r /app/build/. /static/
