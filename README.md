# Apa Sebenarnya Berlaku Pada Roti Dalam Laci?

Video animasi asli **Sains Tahun 6 · Unit 3 Mikroorganisma**. Semua visual, muzik dan kesan bunyi dijana oleh kod. Narasi kini menggunakan enjin TTS neural percuma apabila tersedia. Tiada API berbayar, kunci API, kredit atau pendaftaran akaun diperlukan.

## Pemasangan pada Mac

Pasang Node.js 25, Python 3.10+ dan ffmpeg (contohnya `brew install node@25 python ffmpeg`). Pastikan `node`, `npm`, `python3`, `ffmpeg` dan `ffprobe` berada dalam PATH. Dalam direktori projek:

```sh
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-voice.txt
npm run voice
npm run preview
npm run render
```

`voice.sh` memilih `.venv/bin/python` secara automatik. Untuk persekitaran Python lain, tetapkan `PYTHON_BIN=/laluan/python`. `npm run voice` mencetak enjin dan suara sebenar, kemudian menghasilkan lapan WAV dan fail JSON dalam `out/voice/`. `preview` dan `render` turut menjalankan langkah suara; cache yang sah mengelakkan permintaan TTS berulang.

- `npm run stills`: lapan PNG 1080×1920 di `out/stills/`.
- `npm run preview`: `out/preview.mp4`, 540×960, 30 fps, H.264 + AAC.
- `npm run render`: `out/mikroorganisma.mp4`, 1080×1920, 30 fps, H.264 + AAC.

Video tanpa suara mengambil kira-kira 80 saat. Dengan suara, tempoh ditentukan oleh WAV sebenar dan mungkin lebih panjang. Tiada audio/video, model, `.venv` atau `node_modules` dimasukkan ke Git.

## Pilihan suara percuma dan keputusan

Semakan sumber pada 30 Oktober 2026:

| Pilihan | Ciri dan batasan | Keputusan projek |
| --- | --- | --- |
| [edge-tts](https://github.com/rany2/edge-tts) | Menggunakan perkhidmatan bacaan Microsoft Edge secara dalam talian; tiada kunci atau akaun. Suara neural Malaysia, kadar/pic/kelantangan dan peristiwa `WordBoundary`. Bukan API rasmi dengan jaminan ketersediaan; akses boleh berubah atau disekat. | Pilihan utama berdasarkan ciri: sesuai untuk prosa naratif dan sari kata bertanda masa. |
| [Meta MMS / VITS](https://github.com/facebookresearch/fairseq/tree/main/examples/mms), [`facebook/mms-tts-zlm`](https://huggingface.co/facebook/mms-tts-zlm) | Model Melayu tempatan pada CPU selepas muat turun. Tiada cap masa perkataan rasmi atau pilihan gaya ekspresif. Lesen model **CC-BY-NC 4.0**, perlu atribusi dan penggunaan bukan komersial. | Sandaran neural; jangan gunakannya untuk video komersial. |
| [Malaya-Speech VITS](https://github.com/mesolitica/malaya-speech/blob/master/malaya_speech/tts.py) | Projek Malaysia dengan pilihan seperti VITS-osman, VITS-yasmin, VITS-haqkiem, VITS-orkid; kod senarai model menunjukkan sokongan tanda baca. Memerlukan model, normalizer serta kebergantungan khusus; lesen perlu disemak bagi setiap checkpoint. | Diteliti tetapi tidak dipilih: integrasi dan keserasian Mac lebih rumit, tiada peristiwa perkataan setara Edge yang disahkan. |
| macOS `say -v Amira` | Tempatan dan ringkas selepas suara sistem dipasang; tiada cap masa perkataan melalui antara muka ini. | Sandaran terakhir bersuara; kurang ekspresif dalam percubaan asal pengguna. |

**Lalai: `ms-MY-OsmanNeural`**, suara lelaki untuk watak Roti yang bersahaja. **`ms-MY-YasminNeural`** ialah alternatif perempuan. Pilihan ini berdasarkan ciri dan kesesuaian watak, bukan keputusan ujian pendengaran A/B yang telah selesai. Katalog Edge dan kualiti sebenar perlu disahkan apabila rangkaian membenarkan; jangan anggap model atau perkhidmatan percuma akan tersedia selama-lamanya.

```sh
# Bandingkan suara menggunakan narasi yang sama; salin output sebelum menjana pilihan kedua.
VOICE=ms-MY-OsmanNeural npm run voice
VOICE=ms-MY-YasminNeural npm run voice
# Pilihan kekal bagi terminal semasa:
export VOICE=ms-MY-OsmanNeural
export VOICE_RATE=-8%
export VOICE_PITCH=-3Hz
export VOICE_VOLUME=+0%
npm run preview
```

Kadar sedikit perlahan dan pic sedikit rendah memberi Roti nada tenang. Teks penuh dihantar tepat tanpa penulisan semula. Selepas menerima cap masa, skrip menambah jeda 320 ms pada elipsis, 75 ms pada koma dan 90 ms pada tanda akhir ayat, hanya di celah perkataan yang sah. Semua cap masa berikutnya dianjak mengikut bilangan sampel yang ditambah. Jika perkhidmatan tidak memberi cap masa yang sesuai, tanda baca asal masih dihantar untuk prosodi enjin.

Edge tidak menyokong SSML tersuai, `express-as`, atau gaya emosi sewenang-wenangnya; projek menggunakan hanya parameter kadar, pic dan kelantangan yang disokong. Kawalan `VOICE_*` prosodi ini khusus untuk Edge. MMS menggunakan kadar 0.92 dengan jeda antara klausa; Amira menggunakan 165 perkataan seminit. Tiada janji gaya lakonan yang tidak disokong oleh enjin.

## Rantaian sandaran dan mod luar talian

Lalai: **Edge → MMS → Amira → tanpa suara**. Enjin perlu berjaya menjana kesemua lapan baris sebelum dipilih; audio separa atau audio lama dibuang apabila semua enjin gagal. Cache bergantung pada teks, tetapan, versi pakej dan kod pemprosesan. `out/voice/manifest.json` merekodkan enjin sebenar, tetapan dan kegagalan. Untuk mencuba semula Edge selepas sambungan pulih, gunakan `VOICE_FORCE=1 npm run voice`.

```sh
# Pilihan: pasang sandaran luar talian pada Mac (muat turun model pada penggunaan pertama).
.venv/bin/python -m pip install -r requirements-voice-offline.txt
VOICE_ENGINE=mms npm run voice
# Linux: pasang torch CPU dahulu untuk mengelakkan pakej CUDA yang besar.
.venv/bin/python -m pip install 'torch>=2.6,<3' --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements-voice-offline.txt
```

MMS dimuatkan ke CPU dengan benih tetap, maksimum empat thread dan `trust_remote_code=False`. Selepas model dicache oleh Hugging Face, ia boleh digunakan tanpa Internet. Tiada token atau log masuk Hugging Face digunakan. Pakej MMS adalah pilihan; tanpa pakej tersebut, rantaian terus mencuba Amira. Pasang Amira melalui tetapan suara macOS, kemudian uji `say -v Amira 'Hai'`.

`VOICE_ENGINE=auto|edge|mms|say|none` memilih titik permulaan rantaian. Contohnya `mms` masih boleh beralih ke Amira. `none` mematikan narasi dan membersihkan WAV lama. `VOICE_REQUIRED=1 npm run preview` menggagalkan arahan jika tiada enjin bersuara berjaya, supaya render senyap tidak disalah anggap berjaya. `VOICE_TIMEOUT=300` menetapkan had saat bagi setiap enjin.

Dalam rangkaian terhad, Edge memerlukan `speech.platform.bing.com` termasuk WebSocket HTTPS. MMS memerlukan `huggingface.co` dan hos muat turun yang digunakan oleh Hugging Face, lazimnya `cdn-lfs.huggingface.co`, `cas-bridge.xethub.hf.co`, `cas-server.xethub.hf.co`. Proksi `HTTPS_PROXY` dan sijil CA sesi dikekalkan; pengesahan TLS tidak dimatikan. Teks narasi dihantar kepada Microsoft jika Edge digunakan; pilih MMS untuk sintesis tempatan.

## Masa, sari kata dan audio

`ffprobe` membaca tempoh WAV yang telah diproses. Setiap babak memberi ruang tambahan 1.2 saat selepas narasi. Fail `out/voice/1.json` hingga `8.json` menyimpan teks tepat, tempoh, enjin dan cap masa perkataan (saat relatif kepada permulaan audio baris). Metadata yang tidak sepadan ditolak. Cap masa sebenar dipadankan kepada perkataan asal, termasuk token yang dipecahkan oleh perkhidmatan, dan digunakan oleh serlahan sari kata. Serlahan berhenti ketika jeda. MMS/Amira atau metadata yang tidak sah menggunakan anggaran; `out/timeline.json` menunjukkan `word-boundary` atau `estimated` bagi setiap babak. Gerakan mulut masih menggunakan RMS audio sebenar.

Narasi melalui high-pass 75 Hz, EQ lembut dan pemampatan nisbah 2:1. Muzik diperlahankan di bawah narasi seperti sebelumnya. Selepas campuran narasi + muzik + kesan bunyi, ffmpeg mengukur dan menormalkan audio dalam **dua laluan** ke sasaran **−14 LUFS**, had true peak −1.5 dBTP dan LRA 11. Selepas dua laluan itu, ukuran disahkan; campuran kesan bunyi dengan puncak besar menerima pembetulan gain dan limiter oversampling berkompensasi kependaman (maksimum empat pembetulan). Render dihentikan jika sasaran masih tersasar. `out/loudness.json` menyimpan ukuran sebelum/selepas serta pembetulan; pengekodan AAC boleh mengubah bacaan sedikit. WAV perantaraan mengekalkan ruang kepala untuk mengelakkan kliping sebelum normalisasi. Penapisan tidak mengubah tempo atau memotong senyap awal, maka cap masa kekal sejajar.

## Pengujian dan status pengesahan

```sh
npm test
npm run test:voice
VOICE_REQUIRED=1 npm run preview
ffmpeg -i out/preview.mp4 -vn -af volumedetect -f null -
# Dengar secara tempatan pada Mac:
afplay out/voice/1.wav
open out/preview.mp4
```

Ujian meliputi tempoh WAV sebenar, cap masa/peralihan sari kata, jeda yang menganjak cap masa, penolakan teks tidak sepadan, rantaian gagal yang membersihkan audio lama, pemprosesan audio, determinisme kesan bunyi dan ukuran −14 LUFS tanpa perubahan tempoh.

**Status sandbox:** kebergantungan Edge serta MMS CPU telah dipasang. Percubaan Edge dan muat turun MMS menerima penolakan proksi `403`; Amira tiada pada Linux. Oleh itu, penjanaan lapan baris neural dan pengesahan pendengaran belum dapat diselesaikan. Ujian tempatan dan render sandaran tanpa suara dijalankan secara berasingan; ia bukan bukti narasi neural berjaya. Domain yang diperlukan telah disimpan dalam draf tetapan persekitaran, tetapi draf itu tidak mengaktifkan akses secara sendiri. Selepas perubahan rangkaian disimpan/diterbitkan, jalankan semula `VOICE_FORCE=1 VOICE_REQUIRED=1 npm run preview`. Node 25 dan suara pada Mac sebenar belum diuji dalam sandbox ini.

## Struktur dan kandungan

`src/characters/` dan `src/scenes/` melukis tujuh watak serta lapan babak asal. `scripts/voice.py` mengendalikan penyesuai enjin, cache, jeda dan pemprosesan WAV; `src/timeline.js` membaca durasi serta cap masa; `src/audio.js` menormalkan campuran; `src/render.js` menyalurkan RGBA mentah ke ffmpeg. Tiada pelayan diperlukan.

Narasi dalam `src/narration.json` dikekalkan tepat. Istilah “jahat” dan “hanya hidup” berasal daripada teks yang dibekalkan; virus memerlukan sel hidup untuk membiak. Jangan makan atau menghidu roti berkulapuk; eksperimen perlu pengawasan guru dan beg perlu kekal tertutup.
