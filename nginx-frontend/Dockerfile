# Use official Nginx image
FROM nginx:stable-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY flaskapp /etc/nginx/conf.d/flaskapp.conf

# Copy static files
COPY static /usr/share/nginx/html/static

# Expose port 80
EXPOSE 80

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
