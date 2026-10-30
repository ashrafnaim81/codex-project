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

## Naik taraf suara

Pasang Python 3.10+, kemudian pada Mac:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-voice.txt
npm run voice
npm run preview
```

Enjin lalai ialah [edge-tts](https://github.com/rany2/edge-tts), menggunakan `ms-MY-OsmanNeural`: suara neural Bahasa Melayu Malaysia yang sesuai sebagai pilihan awal untuk Roti. Ia percuma tanpa akaun atau kunci tetapi memerlukan Internet dan bergantung pada perkhidmatan Edge yang boleh berubah. Alternatif `VOICE=ms-MY-YasminNeural npm run voice` memilih suara perempuan; Osman ialah suara lelaki. Pilihan ini berdasarkan ciri, bukan perbandingan pendengaran A/B yang telah disahkan dalam sandbox.

Kadar lalai `-8%`, pic `-3Hz` dan kelantangan `+0%` boleh diubah dengan `VOICE_RATE`, `VOICE_PITCH`, `VOICE_VOLUME`. Teks asal dihantar tanpa penulisan semula; apabila cap masa tersedia, jeda lembut ditambah selepas elipsis dan koma dan cap masa dianjak. Edge membenarkan kawalan prosodi tersebut tetapi [tidak menyokong SSML tersuai](https://github.com/rany2/edge-tts#custom-ssml). Tiada kawalan emosi tambahan dijanjikan.

Rantaian automatik: Edge → [Meta MMS Malay](https://huggingface.co/facebook/mms-tts-zlm) pada CPU → `say -v Amira` → tiada suara. Enjin yang berjaya mesti menjana semua lapan baris; baris separa dan audio lama dibuang jika semua enjin gagal. `VOICE_ENGINE=auto|edge|mms|say|none` memilih titik mula. `VOICE_REQUIRED=1 npm run preview` menghentikan render jika tiada suara. Untuk memasang sandaran MMS pilihan:

```sh
.venv/bin/python -m pip install -r requirements-voice-offline.txt
VOICE_ENGINE=mms npm run voice
```

MMS perlu memuat turun model sekali, kemudian boleh berjalan luar talian. Model MMS berlesen [CC-BY-NC 4.0](https://github.com/facebookresearch/fairseq/tree/main/examples/mms#license), dengan syarat atribusi dan penggunaan bukan komersial. [Malaya-Speech](https://github.com/mesolitica/malaya-speech/blob/master/malaya_speech/tts.py) juga menyediakan model VITS Bahasa Melayu seperti Osman dan Yasmin; pemasangan dan lesen checkpoint perlu diteliti satu per satu. Ia tidak dipilih kerana tiada cap masa perkataan yang disahkan dan setup model lebih rumit. MMS dan Amira tidak membekalkan cap masa perkataan dalam integrasi ini.

Edge menyimpan cap masa perkataan dalam `out/voice/*.json`; serlahan menggunakan masa tersebut apabila teks sepadan, dan anggaran digunakan jika tidak. `ffprobe` membaca durasi WAV sebenar. Suara menerima high-pass, EQ lembut dan pemampatan; muzik masih direndahkan ketika suara bermain. Campuran dinormalkan ke sekitar −14 LUFS dengan pengukuran ffmpeg; `out/loudness.json` merekodkan ukuran. Hasil AAC boleh berbeza sedikit. Audio, video dan `.venv` tidak dikomit.

Dalam sandbox ini, proksi menolak akses kepada `speech.platform.bing.com` dan `huggingface.co` dengan HTTP 403, dan `say` tiada. Oleh itu suara neural, cap masa sebenar serta main balik narasi belum dapat disahkan di sini. Selepas akses rangkaian dibenarkan, jalankan `VOICE_REQUIRED=1 npm run preview` dan dengarkan `out/preview.mp4`. Jangan matikan pengesahan TLS.
