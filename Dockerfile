FROM node:24-slim
WORKDIR /app

ENV NODE_ENV=production \
    STANDALONE=false \
    HOST=0.0.0.0

ARG APP_VERSION=0.1.4
RUN npm install --omit=dev "@truefoundry/trueforge@${APP_VERSION}" \
    && npm cache clean --force

RUN groupadd --gid 10001 trueforge \
    && useradd --uid 10001 --gid trueforge --shell /usr/sbin/nologin trueforge

EXPOSE 8790
USER 10001:10001
CMD ["node", "node_modules/@truefoundry/trueforge/dist/main.js"]
