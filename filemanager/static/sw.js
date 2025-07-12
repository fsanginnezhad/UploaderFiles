const CACHE_NAME = 'my-pwa-cache-v1';
const urlsToCache = [
  "/",
  "{% static 'accounts/css/admin_manage_photos.css' %}",
  "{% static 'accounts/css/admin_page.css' %}",
  "{% static 'accounts/css/login.css' %}",
  "{% static 'accounts/css/user_list.css' %}",
  "{% static 'accounts/css/user_page.css' %}",
  "{% static 'filemanager/css/file_upload.css' %}",
  "{% static 'accounts/js/script.js' %}",
  "{% static 'accounts/js/user_list.js' %}",
  "{% static 'filemanager/js/script.js' %}",
  "{% static 'icons/Enter.png' %}",
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});