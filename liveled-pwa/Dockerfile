FROM nginx:1.27-alpine
COPY liveled-pwa/nginx.conf /etc/nginx/conf.d/default.conf
COPY liveled-pwa/index.html liveled-pwa/app.css liveled-pwa/app.js liveled-pwa/sw.js liveled-pwa/manifest.webmanifest /usr/share/nginx/html/
COPY liveled-pwa/icons /usr/share/nginx/html/icons
EXPOSE 80
