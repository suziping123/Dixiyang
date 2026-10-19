# syntax=docker/dockerfile:1
# Dixiyang Vue 前端：Node 构建 + Nginx 静态托管/反向代理
FROM node:22-alpine AS build

# 国内网络可在 .env 设置 NPM_REGISTRY=https://registry.npmmirror.com
ARG NPM_REGISTRY=https://registry.npmjs.org
WORKDIR /app

COPY dixiyang-vue/Dixiyang-vue3/package.json dixiyang-vue/Dixiyang-vue3/package-lock.json ./
RUN npm config set registry "${NPM_REGISTRY}" \
    && npm ci --no-audit --no-fund

COPY dixiyang-vue/Dixiyang-vue3/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/healthz || exit 1
