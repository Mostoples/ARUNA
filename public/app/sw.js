/* ARUNA app — service worker sederhana: cache aset statis, jaringan dulu untuk sisanya. */
const VERSION = "aruna-app-v3";
const ASSETS = ["./", "index.html", "app.css", "app.js", "img/mesin.png", "img/icon-192.png", "manifest.webmanifest"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(VERSION).then((c) => c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;   // Firebase & CDN langsung ke jaringan
  e.respondWith(fetch(e.request).then((r) => {
    const copy = r.clone();
    caches.open(VERSION).then((c) => c.put(e.request, copy));
    return r;
  }).catch(() => caches.match(e.request)));
});
