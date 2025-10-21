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

# Copy the build output from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to the outside world
EXPOSE 80

# The default Nginx command will start the server
CMD ["nginx", "-g", "daemon off;"]