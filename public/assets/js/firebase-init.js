/* ARUNA — inisialisasi Firebase (SDK modular via CDN gstatic, tanpa bundler).
   Impor dari file lain:
     import { app, auth, rtdb, db } from "./firebase-init.js";
   Catatan: file yang mengimpor ini harus dimuat dengan <script type="module">. */

import { initializeApp } from "https://www.gstatic.com/firebasejs/12.16.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInAnonymously,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  onAuthStateChanged,
  signOut
} from "https://www.gstatic.com/firebasejs/12.16.0/firebase-auth.js";
import {
  getDatabase,
  ref,
  onValue,
  set,
  update,
  get
} from "https://www.gstatic.com/firebasejs/12.16.0/firebase-database.js";
import {
  getFirestore,
  doc,
  setDoc,
  getDoc,
  serverTimestamp
} from "https://www.gstatic.com/firebasejs/12.16.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCbh0YPIdFsUc74VAZFFvU8D4a-6J3V9Qw",
  authDomain: "aruna-id.firebaseapp.com",
  databaseURL: "https://aruna-id-default-rtdb.firebaseio.com",
  projectId: "aruna-id",
  storageBucket: "aruna-id.firebasestorage.app",
  messagingSenderId: "827923985045",
  appId: "1:827923985045:web:789702a8fa4cd4d109a19c"
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const rtdb = getDatabase(app);   // telemetri alat (real-time)
export const db = getFirestore(app);    // profil, konten, penelitian, chat
export const googleProvider = new GoogleAuthProvider();

// Re-export helper agar halaman lain cukup impor dari satu file ini
export {
  // Auth
  signInWithPopup,
  signInAnonymously,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  onAuthStateChanged,
  signOut,
  // Realtime Database (telemetri alat)
  ref,
  onValue,
  set,
  update,
  get,
  // Firestore (profil, konten)
  doc,
  setDoc,
  getDoc,
  serverTimestamp
};

/* Penjaga halaman: panggil requireAuth() di halaman yang wajib login.
   Jika belum login, pengguna diarahkan ke halaman login. */
export function requireAuth(redirectTo = "login.html") {
  return new Promise((resolve) => {
    onAuthStateChanged(auth, (user) => {
      if (user) resolve(user);
      else window.location.href = redirectTo;
    });
  });
}
