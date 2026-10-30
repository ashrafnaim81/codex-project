# Mikroorganisma · Sains Tahun 6

Video animasi 9:16, 30 fps, dijana sepenuhnya menggunakan kod: watak, latar, peralihan, muzik dan kesan bunyi. Semua teks narasi dalam `src/lines.json` dikekalkan seperti skrip.

## Mac

Pasang Node.js 25 dan ffmpeg (contohnya `brew install node@25 ffmpeg`), kemudian jalankan dalam direktori projek:

```sh
npm ci
npm run stills
npm run preview
npm run render
```

`stills` menyimpan lapan PNG di `out/stills`; `preview` menghasilkan `out/preview.mp4` pada 540×960; `render` menghasilkan `out/mikroorganisma.mp4` pada 1080×1920 dengan video H.264 dan audio AAC. Fail WAV kesan bunyi dan campuran disimpan di `out/`. Output dan dependencies tidak dimasukkan ke Git.

`voice.sh` menggunakan suara macOS `say -v Amira`; pasang Amira dalam tetapan sistem jika perlu. Pada Linux ia menggunakan `espeak-ng -v ms` jika tersedia. Jika kedua-duanya tiada, ia membersihkan WAV lama dan meneruskan tanpa suara. `ffprobe` membaca durasi setiap WAV untuk menetapkan tempoh babak. Muzik direndahkan di bawah suara dan mulut mengikut aras audio. Serlahan perkataan adalah anggaran masa seragam; bukan cap masa fonem sebenar.

`src/characters/` mengandungi watak; `src/scenes/scene1.js` hingga `scene8.js` mengandungi babak; `src/icons.js`, `src/sfx.js`, `src/music.js`, `src/timeline.js` dan `src/render.js` mengandungi ilustrasi, sintesis dan aliran render. Bunyi hingar dan zarah ditentukan oleh formula indeks dan masa, tanpa aset luaran atau API.

Dalam sandbox Linux tanpa `say` dan `espeak-ng`, preview boleh disemak tanpa suara; narasi Mac perlu diuji pada mesin yang mempunyai Amira.
