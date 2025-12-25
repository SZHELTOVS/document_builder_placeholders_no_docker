# Development Dockerfile для Quasar
FROM node:18-alpine

WORKDIR /app

# Копируем package файлы
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci --no-audit --no-fund --ignore-scripts

# Копируем исходный код
COPY . .

# Готовим Quasar (если нужно)
RUN npx quasar prepare 2>/dev/null || echo "Quasar prepare skipped"

EXPOSE 9000

# Запускаем dev сервер
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "9000"]