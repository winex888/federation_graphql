FROM node:8.11.1

ARG NPM_REGISTRY="http://nexus.centr.m:8081/repository/npm-registry/"
ARG VERSION
ARG COMMIT

WORKDIR /app
ENV PORT=8200 \
    SCHEMA_REGESTRY_HOST='localhost' \
    SCHEMA_REGESTRY_PORT=8305 \
    SCHEMA_REGESTRY_URL='/schema'
ENV NPM_CONFIG_LOGLEVEL warn
LABEL ru.kronshtadt.version="$VERSION"
LABEL ru.kronshtadt.commit="$COMMIT"
EXPOSE 8200
COPY . .
RUN npm install --unsafe-perm
CMD ["node", "src/index.js"]
# CMD [ "npm", "start"]