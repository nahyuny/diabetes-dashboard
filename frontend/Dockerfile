# 빌드 스테이지
FROM node:16-alpine as build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# 실행 스테이지
FROM nginx:alpine

# 빌드된 앱을 Nginx 서빙 디렉토리로 복사
COPY --from=build /app/build /usr/share/nginx/html

# Nginx 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]