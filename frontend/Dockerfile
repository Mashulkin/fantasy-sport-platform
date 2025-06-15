# Node.js Docker build for Vue.js frontend application.

# Creates development environment with hot reloading
# and all necessary dependencies.

FROM node:18-alpine

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy application source code
COPY . .

# Expose development server port
EXPOSE 3000

# Start development server with host binding for Docker
CMD ["npm", "run", "dev", "--", "--host"]
