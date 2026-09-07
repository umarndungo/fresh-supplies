FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

EXPOSE 3000

# Dev mode: the repo root and a named node_modules volume are mounted by
# docker-compose.yml; this container runs `next dev` with live reload across
# the host bind mount.
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]