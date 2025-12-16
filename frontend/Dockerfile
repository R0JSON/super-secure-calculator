# frontend/Dockerfile

# ---- Stage 1: Build the React App ----
# Use an official Node.js runtime as the builder image
FROM node:20-alpine as builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm ci

# 2. CIS 4.6 (Efficiency): Clear the npm cache after installing packages
RUN npm cache clean --force

# Copy the rest of the application's source code
COPY . .

# Argument to pass the API URL at build time
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build the app for production
RUN npm run build

# ---- Stage 2: Serve the App with Nginx ----
# Use a lightweight Nginx image
FROM nginx:stable-alpine

# 3. CIS 5.7 (Reliability): Copy the build output, ensuring the non-root 'nginx' user owns the files
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 1. CIS 5.7 (Security): Ensure the container is run as the non-root user
USER nginx

# Expose port 80 to the outside world
EXPOSE 80

# The default Nginx command will start the server
CMD ["nginx", "-g", "daemon off;"]
