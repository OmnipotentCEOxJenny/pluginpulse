# PluginPulse

![PluginPulse logo](assets/logo.png)

PluginPulse is a free, read-only tracker of **public** plugin data. Once a day it takes a snapshot of the official MCP Registry, GitHub stars, forks and releases for the repos you choose, and the public marketplace page at https://x.ai/bot/marketplace. Once a week it writes a **Movers & Shakers** digest: what is new, what was updated, what is rising by star growth, and how many listings each category has. Every number names its source and its capture time in Eastern Time (ET). It makes no install or rating claims.

## Project status: done, pending, uncertain
**Done**
- 2026-10-20: v1.0.0 built and tested with live data: a real snapshot (MCP Registry, 8 GitHub repos, the marketplace page; 38 requests, all HTTP 200 except `releases/latest` 404 for repos that have tags but no GitHub Release, reported as "no GitHub Release"; on day one the registry read hit the 20-page cap and is labeled partial), a real digest, manifest valid JSON, skill frontmatter valid, every file link resolves. Example in `examples/`.
- Publisher terms read (Cursor Marketplace Publisher Terms, last updated May 6, 2026): no conflict found. PluginPulse is free, MIT-licensed, collects only what its stated function needs and makes no unsubstantiated claims.

**Pending**
- Marketplace submission: not submitted yet.
- Translated summaries below are machine-made and not reviewed by native speakers. Corrections welcome through an issue.
- "Rising" needs 7 or more days of daily snapshots before it ranks anything.

**Uncertain**
- The marketplace page is read from data embedded in the public page, not a documented API. If its layout changes, PluginPulse reports "page layout changed" rather than guessing.
- The marketplace currently shows `installCount: 0` for every listing, so installs cannot be measured. PluginPulse does not rank by installs.
- How listings work on the Grok Bot and Grok side: not described in the publisher terms.

## Quick start
1. `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt`
2. Daily: `.venv/bin/python scripts/pluginpulse.py snapshot --contact mailto:you@example.com`
3. Weekly: `.venv/bin/python scripts/pluginpulse.py digest`
4. Or just ask: "Take today's PluginPulse snapshot" or "Who are this week's movers and shakers?"

## Installation
Install from this repository: https://github.com/OmnipotentCEOxJenny/pluginpulse (Cursor plugin format: `.cursor-plugin/plugin.json`, `skills/`, `rules/`). Python 3.10+ and one pinned free dependency (`requests==2.32.3`). No API keys, no accounts, no paid services.

## Data sources and limits
| Source | How | Limits honored |
|---|---|---|
| MCP Registry `https://registry.modelcontextprotocol.io/v0/servers` | Official public API, paged (`limit=100`, `cursor`), `version=latest`, `updated_since` (default 8 days) | 1 request per second, max 20 pages per run (marked partial if reached) |
| GitHub REST API | Unauthenticated `repos/{owner}/{repo}` and `releases/latest` | Budget of 50 requests per run, under GitHub's 60 per hour; stops on 403 |
| https://x.ai/bot/marketplace | robots.txt checked first (it allows `/bot/`), one page request | User-Agent `PluginPulse/1.0.0 (+contact)`, Retry-After honored on 429/503, stops if asked to wait over 10 minutes |

Only minimal marketplace fields are kept (id, name, creator handle, categories, updated date). Descriptions and images are not copied, and the digest links back to the listings instead of republishing them.

## Testing
1. Run the snapshot command above with your contact. Expected: `snapshot-YYYY-MM-DD.json` with `captured_et` for each source and a `request_log`.
2. Run the digest command. Expected: `digest-YYYY-MM-DD.md` with registry new/updated counts, repo stars and releases, "Rising: not enough history yet" on day one, and marketplace category counts with a link back.
3. Compare with `examples/digest-2026-10-20.md`.

## Privacy
PluginPulse runs on your machine and sends nothing anywhere except the read requests listed above. It collects no data about its users.

## Credits
- Inventor and publisher: Rob Domaine / Omnipotent Media LLC
- Builder: Jenny Echo

## Rob Domaine's four pillars
1. Trustworthy, honest, real data, truthful: every number is sourced and timed; nothing is estimated.
2. Use only legitimate means: official APIs and robots.txt-allowed pages only, with honest identification.
3. Double-check everything: each digest number is checked against its snapshot.
4. Stay within the law and rules always: local, county, state, federal and platform rules.

## Components
- `scripts/pluginpulse.py`: snapshot and digest commands.
- `scripts/repos.txt`: GitHub repos to track.
- `scripts/requirements.txt`: pinned dependency.
- `skills/pluginpulse-snapshot`: taking and checking a daily snapshot.
- `skills/movers-and-shakers`: building and summarizing the weekly digest.
- `rules/pillars-and-scope.mdc`: the pillars and scope.
- `examples/digest-2026-10-20.md`: a real digest from the first test run.

## Languages
These summaries are machine-made translations and have not been reviewed by native speakers. The English text is authoritative.

- **Español:** PluginPulse es un plugin gratuito de solo lectura que toma instantáneas diarias de datos públicos de plugins y publica un resumen semanal, con la fuente y la hora de cada número.
- **Français:** PluginPulse est un plugin gratuit en lecture seule qui prend chaque jour un instantané de données publiques sur les plugins et produit un résumé hebdomadaire, avec la source et l'heure de chaque chiffre.
- **Deutsch:** PluginPulse ist ein kostenloses, rein lesendes Plugin, das täglich öffentliche Plugin-Daten erfasst und eine wöchentliche Übersicht erstellt, mit Quelle und Uhrzeit zu jeder Zahl.
- **Português:** PluginPulse é um plugin gratuito, somente leitura, que registra diariamente dados públicos de plugins e gera um resumo semanal, com a fonte e o horário de cada número.
- **Italiano:** PluginPulse è un plugin gratuito di sola lettura che acquisisce ogni giorno dati pubblici sui plugin e crea un riepilogo settimanale, con fonte e orario di ogni numero.
- **Nederlands:** PluginPulse is een gratis, alleen-lezen plug-in die dagelijks openbare plug-ingegevens vastlegt en een wekelijks overzicht maakt, met bron en tijdstip bij elk getal.
- **Polski:** PluginPulse to darmowa wtyczka tylko do odczytu, która codziennie zapisuje publiczne dane o wtyczkach i tworzy cotygodniowe podsumowanie, ze źródłem i czasem każdej liczby.
- **Русский:** PluginPulse — бесплатный плагин только для чтения, который ежедневно сохраняет публичные данные о плагинах и составляет еженедельную сводку с источником и временем каждой цифры.
- **Українська:** PluginPulse — безкоштовний плагін лише для читання, що щодня зберігає публічні дані про плагіни й складає щотижневий огляд із джерелом і часом кожного числа.
- **Türkçe:** PluginPulse, herkese açık eklenti verilerinin günlük anlık görüntüsünü alan ve her sayının kaynağını ve saatini belirten haftalık bir özet hazırlayan ücretsiz, salt okunur bir eklentidir.
- **العربية:** PluginPulse إضافة مجانية للقراءة فقط تلتقط يوميًا بيانات عامة عن الإضافات وتعدّ ملخصًا أسبوعيًا، مع ذكر مصدر كل رقم ووقت التقاطه.
- **עברית:** PluginPulse הוא תוסף חינמי לקריאה בלבד שמצלם מדי יום נתונים ציבוריים על תוספים ומפיק סיכום שבועי, עם המקור והשעה של כל מספר.
- **فارسی:** PluginPulse افزونه‌ای رایگان و فقط‌خواندنی است که هر روز از داده‌های عمومی افزونه‌ها تصویر می‌گیرد و خلاصه‌ای هفتگی با منبع و زمان هر عدد تهیه می‌کند.
- **हिन्दी:** PluginPulse एक मुफ़्त, केवल-पढ़ने वाला प्लगइन है जो रोज़ सार्वजनिक प्लगइन डेटा का स्नैपशॉट लेता है और हर संख्या के स्रोत व समय के साथ साप्ताहिक सारांश बनाता है।
- **বাংলা:** PluginPulse একটি বিনামূল্যের, শুধু-পড়ার প্লাগইন, যা প্রতিদিন প্রকাশ্য প্লাগইন ডেটার স্ন্যাপশট নেয় এবং প্রতিটি সংখ্যার উৎস ও সময়সহ সাপ্তাহিক সারাংশ তৈরি করে।
- **اردو:** PluginPulse ایک مفت، صرف پڑھنے والا پلگ اِن ہے جو روزانہ عوامی پلگ اِن ڈیٹا کا اسنیپ شاٹ لیتا ہے اور ہر عدد کے ماخذ اور وقت کے ساتھ ہفتہ وار خلاصہ بناتا ہے۔
- **中文（简体）:** PluginPulse 是一款免费的只读插件，每天记录公开的插件数据并生成每周摘要，每个数字都注明来源和采集时间。
- **日本語:** PluginPulse は、公開されているプラグインのデータを毎日記録し、各数値の出典と取得時刻を付けた週間まとめを作る無料の読み取り専用プラグインです。
- **한국어:** PluginPulse는 공개 플러그인 데이터를 매일 기록하고 모든 숫자에 출처와 수집 시각을 표시한 주간 요약을 만드는 무료 읽기 전용 플러그인입니다.
- **Bahasa Indonesia:** PluginPulse adalah plugin gratis hanya-baca yang mencatat data plugin publik setiap hari dan membuat ringkasan mingguan, lengkap dengan sumber dan waktu setiap angka.
- **Tiếng Việt:** PluginPulse là plugin miễn phí, chỉ đọc, ghi lại dữ liệu công khai về plugin mỗi ngày và tạo bản tóm tắt hằng tuần, kèm nguồn và thời điểm của từng con số.
- **Kiswahili:** PluginPulse ni programu-jalizi ya bure ya kusoma tu inayonasa kila siku data ya umma ya programu-jalizi na kutoa muhtasari wa kila wiki, ikitaja chanzo na wakati wa kila nambari.

## License
MIT. See `LICENSE`.
