# Nginx reverse proxy configuration.

# Sets up Nginx as a reverse proxy for frontend and backend services
# with proper routing and WebSocket support.

FROM nginx:1.25-alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose HTTP port
EXPOSE 80

# Start Nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]
