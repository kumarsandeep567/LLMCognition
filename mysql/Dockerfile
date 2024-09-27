# Use the official MySQL image from Docker Hub
FROM mysql:8.0

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD {$MYSQL_ROOT_PASSWORD}
ENV MYSQL_DATABASE {$MYSQL_DATABASE}

# Expose the default MySQL port
EXPOSE 3306

# Copy initialization SQL scripts (if any)
# COPY ./init.sql /docker-entrypoint-initdb.d/

# By default, MySQL will be started by the base image ENTRYPOINT
