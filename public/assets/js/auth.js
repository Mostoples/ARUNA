/* ARUNA — penjaga autentikasi halaman aplikasi (module).
   - Belum login → dialihkan ke login.html
   - Mengisi inisial avatar & identitas pengguna ([data-user-name]/[data-user-email])
   - Menangani tombol/tautan keluar ([data-logout]) */
import { auth, db, onAuthStateChanged, signOut, doc, getDoc } from "./firebase-init.js";

onAuthStateChanged(auth, async (user) => {
  if (!user) { location.replace("login.html"); return; }

  let nama = user.displayName ||
    (user.isAnonymous ? "Tamu" : (user.email || "Pengguna").split("@")[0]);
  let sekolah = null;

  // Lengkapi dari profil Firestore bila ada
  try {
    const snap = await getDoc(doc(db, "users", user.uid));
    if (snap.exists()) {
      const d = snap.data();
      if (d.nama) nama = d.nama;
      if (d.sekolah) sekolah = d.sekolah;
    }
  } catch (e) { /* offline / rules — pakai data auth saja */ }

  const inisial = (nama.trim()[0] || "A").toUpperCase();
  document.querySelectorAll(".avatar").forEach((el) => { el.textContent = inisial; el.title = nama; });
  document.querySelectorAll("[data-user-name]").forEach((el) => { el.textContent = nama; });
  document.querySelectorAll("[data-user-email]").forEach((el) => {
    el.textContent = user.email || (user.isAnonymous ? "Mode tamu (anonim)" : "—");
  });
  document.querySelectorAll("[data-user-school]").forEach((el) => {
    el.textContent = sekolah || (user.isAnonymous ? "Jelajah bebas" : "Sekolah belum diisi");
  });
  document.querySelectorAll("[data-greet-name]").forEach((el) => { el.textContent = nama; });
  document.dispatchEvent(new CustomEvent("aruna:user", { detail: { user, nama, sekolah } }));
});

document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-logout]");
  if (!t) return;
  e.preventDefault();
  signOut(auth).finally(() => location.replace("index.html"));
});
