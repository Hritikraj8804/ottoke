FROM nginxinc/nginx-unprivileged:alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy all static assets into the default Nginx public directory
COPY . /usr/share/nginx/html/

# Expose non-privileged HTTP port
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
