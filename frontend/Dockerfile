# Imagen del frontend (PHP 8.2 + Apache). Contexto de construcción: carpeta frontend/.
FROM php:8.2-apache

ENV APACHE_DOCUMENT_ROOT=/var/www/html/public \
    PORT=8080 \
    TZ=America/Guatemala

# Raíz web en public/ y puerto tomado de la variable PORT (Render la define al arrancar)
RUN sed -ri 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf \
    && sed -ri 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf \
    && sed -ri 's!Listen 80!Listen ${PORT}!' /etc/apache2/ports.conf \
    && sed -ri 's!<VirtualHost \*:80>!<VirtualHost *:${PORT}>!' /etc/apache2/sites-available/000-default.conf \
    && echo 'PassEnv API_URL' > /etc/apache2/conf-available/precalifica-env.conf \
    && echo 'ServerName localhost' >> /etc/apache2/conf-available/precalifica-env.conf \
    && a2enconf precalifica-env \
    && cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" \
    && echo 'date.timezone = America/Guatemala' > "$PHP_INI_DIR/conf.d/zona-horaria.ini"

COPY includes/ /var/www/html/includes/
COPY public/ /var/www/html/public/

EXPOSE 8080
