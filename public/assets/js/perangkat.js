/* ARUNA — Manajemen perangkat & Web Bluetooth (ESP32).
   Pemindaian BLE memakai Web Bluetooth API (Chrome/Edge, wajib HTTPS).
   UUID service ESP32 disesuaikan dengan firmware BIOSYNC pada tahap
   integrasi; provisioning menulis SSID/pass ke characteristic GATT. */
(function () {
  "use strict";

  // UUID layanan provisioning kustom BIOSYNC (contoh — samakan dgn firmware)
  var SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"; // Nordic UART Service

  var btnScan = document.getElementById("btnScan");
  var status = document.getElementById("btStatus");
  var ssid = document.getElementById("ssid");
  var pass = document.getElementById("wifipass");
  var btnKirim = document.getElementById("btnKirim");
  var device = null;

  function setStatus(cls, label) {
    status.className = "chip " + (cls || "");
    status.innerHTML = '<span class="dot"></span> ' + label;
  }

  function setFormEnabled(on) {
    ssid.disabled = !on;
    pass.disabled = !on;
    btnKirim.disabled = !on;
  }

  btnScan.addEventListener("click", function () {
    if (!("bluetooth" in navigator)) {
      window.arunaToast("Browser ini belum mendukung Web Bluetooth — gunakan Chrome/Edge 🙏");
      return;
    }
    setStatus("chip--warn", "Memindai…");
    navigator.bluetooth.requestDevice({
      filters: [{ namePrefix: "BIOSYNC" }, { namePrefix: "ARUNA" }],
      optionalServices: [SERVICE_UUID]
    }).then(function (dev) {
      device = dev;
      setStatus("chip--good", "Terhubung: " + (dev.name || "ESP32"));
      setFormEnabled(true);
      window.arunaToast("Terhubung ke " + (dev.name || "perangkat") + " ✅");
      dev.addEventListener("gattserverdisconnected", function () {
        setStatus("", "Terputus");
        setFormEnabled(false);
      });
      // Tahap integrasi: dev.gatt.connect() → getPrimaryService(SERVICE_UUID)
      // → characteristic.writeValue(SSID/pass terenkode).
    }).catch(function (err) {
      setStatus("", "Terputus");
      if (String(err).indexOf("User cancelled") !== -1 || err.name === "NotFoundError") {
        window.arunaToast("Pemindaian dibatalkan — tidak ada perangkat dipilih");
      } else {
        window.arunaToast("Bluetooth gagal: " + (err.message || err));
      }
    });
  });

  document.getElementById("wifiForm").addEventListener("submit", function (e) {
    e.preventDefault();
    if (!ssid.value.trim()) { window.arunaToast("Isi nama WiFi dulu ya"); return; }
    btnKirim.disabled = true;
    setTimeout(function () {
      btnKirim.disabled = false;
      window.arunaToast("Kredensial WiFi dikirim ke " + (device && device.name || "alat") +
        " — penulisan GATT aktif pada tahap integrasi 📡");
    }, 900);
  });

  document.getElementById("claimForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var kode = e.target.querySelector("input").value.trim();
    if (!kode) { window.arunaToast("Masukkan kode klaim dulu ya"); return; }
    window.arunaToast("Kode “" + kode + "” diverifikasi ke Firestore pada tahap integrasi 🔑");
  });
})();
