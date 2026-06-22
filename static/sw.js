const CACHE_NAME =
'expense-tracker-v1';

const urlsToCache = [

    '/',

    '/login',

    '/signup',

    '/static/manifest.json'
];


// INSTALL SERVICE WORKER

self.addEventListener(
'install',
event => {

event.waitUntil(

caches.open(CACHE_NAME)

.then(cache => {

return cache.addAll(
urlsToCache
);

})

);

});


// FETCH CACHE

self.addEventListener(
'fetch',
event => {

event.respondWith(

caches.match(event.request)

.then(response => {

return response ||
fetch(event.request);

})

);

});


// ACTIVATE

self.addEventListener(
'activate',
event => {

event.waitUntil(

caches.keys()

.then(cacheNames => {

return Promise.all(

cacheNames.map(cache => {

if (cache !== CACHE_NAME) {

return caches.delete(cache);

}

})

);

})

);

});