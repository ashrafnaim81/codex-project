# Apa Sebenarnya Berlaku Pada Roti Dalam Laci?

Projek video animasi asli untuk **Sains Tahun 6 · Unit 3 Mikroorganisma**. Semua bingkai, watak, ikon, muzik dan kesan bunyi dijana oleh kod. Tiada API berbayar, aset stok, atau perkhidmatan AI digunakan.

## Keperluan dan pemasangan pada Mac

Pasang Node.js 25 dan ffmpeg (contohnya `brew install node@25 ffmpeg`). Pastikan `node`, `npm`, `ffmpeg` dan `ffprobe` tersedia dalam PATH. Kemudian, dalam direktori projek:

```sh
npm ci
npm run stills
npm run preview
npm run render
```

`stills` menyimpan lapan PNG 1080×1920 dalam `out/stills/`. `preview` menghasilkan `out/preview.mp4` pada 540×960, 30 fps. `render` menghasilkan `out/mikroorganisma.mp4` pada 1080×1920, 30 fps, H.264 + AAC. Video tanpa suara mengambil kira-kira 80 saat; dengan suara, tempohnya mengikut bacaan sebenar. Output dan node_modules tidak dimasukkan dalam Git. Hentikan render menggunakan Ctrl-C jika perlu.

## Narasi tempatan

`voice.sh` menjana satu WAV bagi setiap baris daripada `src/narration.json`, tanpa mengubah teks. Pada macOS, pasang suara Melayu **Amira** melalui tetapan sistem dan uji `say -v Amira 'Hai'`. Skrip menggunakan `say -v Amira` dan menukar AIFF kepada WAV. Pada Linux, pasang `espeak-ng` (contohnya `sudo apt install espeak-ng`); skrip menggunakan `espeak-ng -v ms`. Jika kedua-duanya tiada, skrip melangkau suara dan memaparkan amaran. Kegagalan suara yang tersedia akan menghentikan render agar ralat tidak disembunyikan.

`ffprobe` membaca tempoh WAV sebenar. Setiap babak memberi ruang tambahan 1.2 saat selepas suara. Muzik diperlahankan sepanjang narasi, dan gerakan mulut menggunakan RMS sampel suara. Sari kata diserlahkan perkataan demi perkataan mengikut anggaran masa seragam dalam baris; ini bukan penjajaran fonem atau pengenalan suara. Masa kemunculan visual juga anggaran mengikut kedudukan frasa. Fail WAV sedia ada boleh digunakan oleh `stills`; render menjana semula suara apabila enjin tersedia. Untuk mod tanpa suara yang bersih, padam hanya `out/voice/` dahulu.

## Struktur

- `src/characters/`: Roti, Yisa, Rizo dan empat cameo mikroorganisma; fungsi menerima masa, mulut dan skala.
- `src/scenes/scene1.js` hingga `scene8.js`: lapan babak berasingan.
- `src/draw.js`, `src/icons.js`: bentuk, teks dan ikon prosedural.
- `src/sfx.js`, `src/music.js`: sintesis WAV mono 24 kHz dengan hingar deterministik.
- `src/timeline.js`: tempoh suara, susunan babak dan teks narasi tepat.
- `src/render.js`: lukisan Canvas, sari kata, campuran audio dan paip RGBA mentah ke ffmpeg dengan kawalan tekanan aliran.

`npm test` menguji pembacaan durasi audio sebenar, kesinambungan garis masa dan determinisme semua kesan bunyi. `out/timeline.json` merekodkan masa bagi render semasa. Tiada nombor rawak tidak berbenih digunakan; hingar dan partikel berasal daripada fungsi indeks deterministik.

## Nota kandungan

Istilah “jahat” dan “hanya hidup” dikekalkan tepat dalam narasi yang dibekalkan. Secara sains, virus memerlukan sel perumah hidup untuk membiak; label visual menggunakan penjelasan ini. Beg berzip hanya digunakan untuk menggambarkan eksperimen, bukan sebagai nasihat menyimpan roti lembap. Jangan makan atau menghidu roti berkulapuk; eksperimen perlu pengawasan guru dan beg perlu kekal tertutup.

Disahkan dalam sandbox dengan Node 24 dan ffmpeg 7; Node 25 pada macOS ialah sasaran tetapi belum diuji pada mesin Mac sebenar. Jika Amira tiada, pasangnya atau gunakan espeak-ng. Tiada proses pelayan diperlukan.
