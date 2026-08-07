FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

ENV VITE_API_BASE=""
RUN npm run build

FROM nginx:stable-alpine
# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf
# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d
# Copy built app
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
