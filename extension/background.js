// Пересилає дані на локальну програму (service worker не впирається в CORS).
// Порт має збігатися з PORT у pulse/constants.py
const ENDPOINT = "http://127.0.0.1:48200/update";

chrome.runtime.onMessage.addListener((data) => {
  fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).catch(() => {});
});
