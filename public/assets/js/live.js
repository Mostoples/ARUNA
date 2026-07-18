/* ARUNA — langganan telemetri real-time dari Firebase RTDB (module).
   Menyebarkan CustomEvent supaya skrip klasik (home.js) bisa ikut memakai:
     aruna:telemetry → devices/{id}/telemetry
     aruna:devstate  → devices/{id}/state
   Jika data belum ada / tanpa izin, halaman tetap jalan dengan simulasi. */
import { rtdb, ref, onValue } from "./firebase-init.js";

const DEVICE_ID = "ARN-2201"; // nanti: dari daftar perangkat milik user

onValue(ref(rtdb, "devices/" + DEVICE_ID + "/telemetry"), (snap) => {
  const t = snap.val();
  if (t) document.dispatchEvent(new CustomEvent("aruna:telemetry", { detail: t }));
}, (err) => console.warn("RTDB telemetry:", err.message));

onValue(ref(rtdb, "devices/" + DEVICE_ID + "/state"), (snap) => {
  const s = snap.val();
  if (s) document.dispatchEvent(new CustomEvent("aruna:devstate", { detail: s }));
}, (err) => console.warn("RTDB state:", err.message));
