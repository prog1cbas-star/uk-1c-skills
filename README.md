# 🇺🇦 uk-1c-skills

> **Українська адаптація AI-agent skills для роботи з 1С:Підприємство / BAF / BAS**  
> на основі upstream-репозиторію [`Nikolay-Shirokov/cc-1c-skills`](https://github.com/Nikolay-Shirokov/cc-1c-skills.git), який підключається як `upstream/cc-1c-skills`.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Upstream](https://img.shields.io/badge/upstream-cc--1c--skills-lightgrey)](https://github.com/Nikolay-Shirokov/cc-1c-skills)
[![Agents](https://img.shields.io/badge/agents-ChatGPT%20%7C%20Claude%20%7C%20Codex%20%7C%20Gemini%20%7C%20Cursor-purple)](#-встановлення-skills)

`uk-1c-skills` — це підтримуваний downstream-репозиторій, який додає український compatibility layer, універсальну структуру для різних AI-агентів і відтворювану build-систему поверх оригінального набору skills для 1С.

Upstream `cc-1c-skills` надає агентам абстракції над XML-форматами, CLI-конфігуратором, CF/CFE/EPF/ERF, керованими формами, ролями, СКД, web-клієнтом та іншими задачами розробки на платформі 1С:Підприємство 8.3. Цей репозиторій не переписує upstream напряму, а накладає українські зміни через `configs/`, `patches/`, `overlays/` і build-пайплайн.

---

## Зміст

- [Що це таке](#-що-це-таке)
- [Що адаптовано для України](#-що-адаптовано-для-україни)
- [Архітектура репозиторію](#-архітектура-репозиторію)
- [Встановлення репозиторію](#-встановлення-репозиторію)
- [Встановлення skills](#-встановлення-skills)
- [Як працювати зі skills](#-як-працювати-зі-skills)
- [Перелік skills](#-перелік-skills)
- [Команди build-системи](#-команди-build-системи)
- [Оновлення upstream](#-оновлення-upstream)
- [Ліцензія](#-ліцензія)

---

## 🇺🇦 Що це таке

`uk-1c-skills` — це українська адаптація skills для AI-агентів, які допомагають розробнику працювати з:

- конфігураціями 1С / BAF / BAS у XML-розвантаженні;
- розширеннями конфігурацій (`.cfe`);
- зовнішніми обробками та звітами (`.epf`, `.erf`);
- керованими формами (`Form.xml`);
- ролями та правами (`Rights.xml`);
- схемами компонування даних (`Template.xml`, СКД/DCS);
- макетами MXL;
- інформаційними базами через CLI конфігуратора;
- web-публікаціями та smoke-тестами web-клієнта.

Репозиторій призначений для команд, які хочуть використовувати оригінальні skills із `cc-1c-skills`, але потребують:

- українських правил сумісності платформ 8.3.x / 8.5.x;
- підтримки BAF/BAS-проєктів;
- універсального layout не тільки для Claude Code;
- контрольованого оновлення upstream без ручних правок у його файлах;
- тестів, CI та документації для довгострокового супроводу.

---

## 🧩 Що адаптовано для України

### 1. UA registry платформ 1С / BAF

Додано machine-readable registry:

```text
configs/platform_versions_ua.yaml
```

У ньому описано відповідність версій платформи до XML-формату та `CompatibilityMode`:

| Платформа | XML format | CompatibilityMode | GeneratedType validation |
|---|---:|---|---|
| `8.3.15` | `2.9` | `Version8_3_15` | strict |
| `8.3.16` | `2.9.1` | `Version8_3_16` | strict |
| `8.3.17` | `2.10` | `Version8_3_17` | strict |
| `8.3.18` | `2.11` | `Version8_3_18` | strict |
| `8.3.19` | `2.12` | `Version8_3_19` | strict |
| `8.3.20` | `2.13` | `Version8_3_20` | tolerant |
| `8.3.21` | `2.14` | `Version8_3_21` | tolerant |
| `8.3.22` | `2.15` | `Version8_3_22` | tolerant |
| `8.3.23` | `2.16` | `Version8_3_23` | tolerant |
| `8.3.24` | `2.17` | `Version8_3_24` | tolerant |
| `8.3.25` | `2.18` | `Version8_3_25` | tolerant |
| `8.3.26` | `2.19` | `Version8_3_26` | tolerant |
| `8.3.27` | `2.20` | `Version8_3_27` | tolerant |
| `8.5.x` | `2.21` | `Version8_5_X` | tolerant |

### 2. Version resolver

Build-система вміє нормалізувати повні версії платформи:

```text
8.3.20      -> 8.3.20
8.3.20.1234 -> 8.3.20
8.3.27.1500 -> 8.3.27
8.5.1       -> 8.5.x
8.5.x       -> 8.5.x
```

Приклад:

```bash
python build/apply.py platform-info 8.3.20
```

Очікуваний зміст відповіді:

```text
Platform: 8.3.20
XML format: 2.13
CompatibilityMode: Version8_3_20
GeneratedType validation: tolerant
Configuration.xml features:
  - StandaloneConfigurationRestrictionRoles
  - InternalInfoContainedObject7
  - URLExternalDataStorage
  - MobileApplicationURLs
  - DefaultReportAppearanceTemplate
  - AllowedIncomingShareRequestTypes
  - DatabaseTablespacesUseMode
```

### 3. Правила `Configuration.xml`

Окремо описано елементи, які зʼявляються в різних версіях платформи:

| Версія | Feature | XML / правило |
|---|---|---|
| `8.3.16+` | `StandaloneConfigurationRestrictionRoles` | `<StandaloneConfigurationRestrictionRoles/>` |
| `8.3.17+` | `InternalInfoContainedObject7` | 7-й `xr:ContainedObject` в `InternalInfo`; `ClassId: fb282519-d103-4dd3-bc12-cb271d631dfc` |
| `8.3.18+` | `URLExternalDataStorage` | `<URLExternalDataStorage/>` |
| `8.3.18+` | `MobileApplicationURLs` | `<MobileApplicationURLs/>` |
| `8.3.20+` | `DefaultReportAppearanceTemplate` | `<DefaultReportAppearanceTemplate/>` |
| `8.3.20+` | `AllowedIncomingShareRequestTypes` | `<AllowedIncomingShareRequestTypes/>` |
| `8.3.20+` | `DatabaseTablespacesUseMode` | `<DatabaseTablespacesUseMode>DontUse</DatabaseTablespacesUseMode>` |

### 4. Поведінка валідатора `GeneratedType`

Для українського compatibility layer зафіксовано різну поведінку валідаторів:

| Версії | Режим | Поведінка |
|---|---|---|
| `8.3.15`–`8.3.19` | strict | невідповідність `GeneratedType name` і `<Name>` є помилкою |
| `8.3.20+`, `8.5.x` | tolerant | невідповідність є попередженням, але не помилкою |

Ці правила не захардкожені довгими `if/else` у Python-коді — вони читаються з `configs/platform_versions_ua.yaml`.

### 5. Універсальні agent adapters

Оригінальний upstream орієнтований переважно на Claude Code і `.claude/skills`. У цьому репозиторії додано універсальну генерацію:

```text
dist/.agents/skills/   # ChatGPT / universal Agent Skills layout
dist/.claude/skills/   # Claude Code
dist/.codex/skills/    # Codex
dist/.gemini/skills/   # Gemini
dist/.cursor/skills/   # Cursor
```

Налаштування агентів зберігаються тут:

```text
configs/agents.yaml
```

Для агентів, які не підтримують Claude-specific metadata, build-система прибирає або адаптує такі поля, не ламаючи сумісність із Claude Code.

---

## 🏗 Архітектура репозиторію

```text
uk-1c-skills/
├── upstream/
│   └── cc-1c-skills/              # upstream як git submodule
├── configs/                       # machine-readable правила
│   ├── agents.yaml
│   ├── build.yaml
│   └── platform_versions_ua.yaml
├── patches/                       # мінімальні git patches до upstream
├── overlays/                      # українські overlays і додаткові skills
├── build/                         # Python build-система
├── tests/                         # pytest-тести
├── docs/                          # документація
├── dist/                          # згенеровані outputs для агентів
└── .agents/skills/                # canonical source-of-truth для UA skills
```

Принциповий підхід:

1. upstream залишається чистим;
2. українські зміни живуть окремо;
3. build бере чистий upstream, застосовує patches та overlays;
4. результат генерується в `dist/`;
5. валідатори перевіряють consistency і agent outputs.

---

## ⚙️ Встановлення репозиторію

### 1. Клонувати downstream

```bash
git clone https://github.com/elftorgcom/uk-1c-skills.git
cd uk-1c-skills
```

### 2. Ініціалізувати upstream submodule

Якщо submodule вже доданий у репозиторії:

```bash
git submodule update --init --recursive
```

Якщо створюєте репозиторій з нуля:

```bash
git submodule add https://github.com/Nikolay-Shirokov/cc-1c-skills.git upstream/cc-1c-skills
git submodule update --init --recursive
```

### 3. Встановити Python-залежності

```bash
python -m pip install -U pip
python -m pip install -e .
python -m pip install pytest PyYAML
```

Мінімальні вимоги:

- Python `3.10+`;
- Git;
- PyYAML;
- pytest.

### 4. Зібрати і перевірити

```bash
python build/apply.py build
python build/apply.py validate
python -m pytest
```

---

## 📦 Встановлення skills

Після збірки всі готові skills лежать у `dist/`.

### ChatGPT / universal Agent Skills layout

```bash
mkdir -p .agents/skills
cp -R dist/.agents/skills/* .agents/skills/
```

Використовуйте цей layout як canonical універсальний формат для агентів, які читають skills із `.agents/skills`.

### Claude Code

```bash
mkdir -p .claude/skills
cp -R dist/.claude/skills/* .claude/skills/
```

Claude Code також може працювати з оригінальним layout upstream `.claude/skills`. Цей downstream зберігає сумісність із Claude-specific `allowed-tools` там, де вони потрібні.

### Codex

```bash
mkdir -p .codex/skills
cp -R dist/.codex/skills/* .codex/skills/
```

### Gemini

```bash
mkdir -p .gemini/skills
cp -R dist/.gemini/skills/* .gemini/skills/
```

### Cursor

```bash
mkdir -p .cursor/skills
cp -R dist/.cursor/skills/* .cursor/skills/
```

### Встановлення одного skill

Наприклад, тільки `form-compile` для Claude Code:

```bash
mkdir -p .claude/skills/form-compile
cp -R dist/.claude/skills/form-compile/* .claude/skills/form-compile/
```

Для UA compatibility layer:

```bash
mkdir -p .agents/skills/ua-1c-platform-compat
cp -R dist/.agents/skills/ua-1c-platform-compat/* .agents/skills/ua-1c-platform-compat/
```

---

## 🧑‍💻 Як працювати зі skills

Skills — це інструкції та допоміжні скрипти для AI-агента. Замість того щоб щоразу пояснювати агенту формат `Configuration.xml`, `Form.xml`, `Rights.xml`, `Template.xml` або CLI-команди конфігуратора, ви підключаєте відповідний skill і даєте задачу бізнесовою мовою.

Приклади запитів:

```text
Використай cf-info і покажи короткий огляд конфігурації з XML-розвантаження.
```

```text
За допомогою form-compile створи керовану форму списку з полями Номенклатура, Кількість, Ціна, Сума.
```

```text
Перевір EPF через epf-validate і врахуй українські правила платформи 8.3.20.
```

```text
Використай skd-edit: додай параметр Період і фільтр по даті в Template.xml.
```

```text
Поясни, які Configuration.xml features потрібні для платформи 8.3.18.
```

Рекомендований workflow:

1. зібрати `dist/` командою `python build/apply.py build`;
2. скопіювати потрібний agent layout у ваш проєкт;
3. відкрити проєкт у відповідному AI-агенті;
4. у задачі явно згадати потрібний skill або тип роботи;
5. після змін запускати валідацію (`cf-validate`, `epf-validate`, `form-validate`, `python build/apply.py validate`).

---

## 🧰 Перелік skills

Нижче наведено skills, які успадковуються з upstream `cc-1c-skills`, а також UA-specific skills, додані в цьому downstream. Опис подано українською, за змістом upstream metadata та призначення кожного skill.

### Конфігурації CF

| Skill | Призначення |
|---|---|
| `cf-init` | Ініціалізувати структуру XML-розвантаження конфігурації 1С. |
| `cf-info` | Показати коротку інформацію про конфігурацію, метадані, версію, vendor, child objects. |
| `cf-edit` | Точково редагувати `Configuration.xml`: властивості конфігурації, версію, vendor, ролі, склад обʼєктів. |
| `cf-validate` | Перевірити коректність XML-розвантаження конфігурації та типові помилки структури. |

### Розширення CFE

| Skill | Призначення |
|---|---|
| `cfe-init` | Ініціалізувати XML-структуру розширення конфігурації. |
| `cfe-borrow` | Додати або оновити запозичені обʼєкти з основної конфігурації в розширенні. |
| `cfe-diff` | Порівняти розширення з базовою конфігурацією та показати відмінності. |
| `cfe-patch-method` | Точково змінити або пропатчити методи модулів у розширенні. |
| `cfe-validate` | Перевірити структуру та узгодженість XML-розширення. |

### Інформаційні бази та CLI конфігуратора

| Skill | Призначення |
|---|---|
| `db-create` | Створити інформаційну базу для розробки або тестування. |
| `db-list` | Показати список доступних інформаційних баз. |
| `db-run` | Запустити інформаційну базу або виконати команду через платформу. |
| `db-update` | Оновити інформаційну базу після завантаження конфігурації. |
| `db-dump-cf` | Вивантажити конфігурацію з бази у CF-файл. |
| `db-dump-xml` | Вивантажити конфігурацію з бази у XML-структуру. |
| `db-load-cf` | Завантажити CF-файл у інформаційну базу. |
| `db-load-xml` | Завантажити XML-розвантаження конфігурації у інформаційну базу. |
| `db-load-git` | Завантажити конфігурацію з git/XML-проєкту у базу. |

### Зовнішні обробки EPF

| Skill | Призначення |
|---|---|
| `epf-init` | Створити мінімальну структуру зовнішньої обробки. |
| `epf-add-form` | Додати керовану форму до зовнішньої обробки. |
| `epf-bsp-init` | Підготувати EPF до використання з підсистемою БСП. |
| `epf-bsp-add-command` | Додати команду БСП для зовнішньої обробки. |
| `epf-build` | Зібрати зовнішню обробку у `.epf`. |
| `epf-dump` | Розвантажити `.epf` у XML/файлову структуру. |
| `epf-validate` | Перевірити зовнішню обробку перед збіркою або передачею користувачу. |

### Зовнішні звіти ERF

| Skill | Призначення |
|---|---|
| `erf-init` | Створити мінімальну структуру зовнішнього звіту. |
| `erf-build` | Зібрати зовнішній звіт у `.erf`. |
| `erf-dump` | Розвантажити `.erf` у XML/файлову структуру. |
| `erf-validate` | Перевірити зовнішній звіт і його XML-структуру. |

### Керовані форми

| Skill | Призначення |
|---|---|
| `form-add` | Додати керовану форму до обʼєкта конфігурації або зовнішньої обробки. |
| `form-compile` | Згенерувати повний `Form.xml` з компактного JSON DSL або з метаданих обʼєкта. |
| `form-edit` | Точково редагувати існуючу керовану форму. |
| `form-info` | Показати структуру форми: елементи, реквізити, команди, події. |
| `form-patterns` | Надати патерни, архетипи та конвенції для проєктування складних форм. |
| `form-remove` | Видалити форму та прибрати посилання на неї з метаданих. |
| `form-validate` | Перевірити `Form.xml`, namespace, елементи, реквізити та типові помилки. |

### Метадані обʼєктів

| Skill | Призначення |
|---|---|
| `meta-compile` | Згенерувати XML метаданих обʼєкта з компактного опису. |
| `meta-edit` | Точково редагувати метадані обʼєкта конфігурації. |
| `meta-info` | Показати інформацію про обʼєкт метаданих. |
| `meta-remove` | Видалити обʼєкт метаданих і повʼязані записи. |
| `meta-validate` | Перевірити XML метаданих обʼєкта та його узгодженість. |

### Ролі та права доступу

| Skill | Призначення |
|---|---|
| `role-compile` | Згенерувати `Rights.xml` ролі з компактного опису прав. |
| `role-info` | Показати зведення прав ролі, RLS і шаблонів доступу. |
| `role-validate` | Перевірити `Rights.xml` ролі на структурні та логічні помилки. |

### СКД / DCS

| Skill | Призначення |
|---|---|
| `skd-compile` | Згенерувати `Template.xml` схеми компонування даних із JSON DSL. |
| `skd-edit` | Точково редагувати СКД: набори даних, поля, параметри, фільтри, варіанти. |
| `skd-info` | Показати короткий огляд структури СКД. |
| `skd-validate` | Перевірити `Template.xml` СКД на структурні та посилальні помилки. |

### MXL-макети

| Skill | Призначення |
|---|---|
| `mxl-compile` | Згенерувати MXL-макет із опису або проміжного формату. |
| `mxl-decompile` | Розібрати MXL-макет у придатний для аналізу формат. |
| `mxl-info` | Показати інформацію про області, колонки, рядки та структуру макета. |
| `mxl-validate` | Перевірити MXL-макет на типові структурні проблеми. |

### Підсистеми, інтерфейс і шаблони

| Skill | Призначення |
|---|---|
| `subsystem-compile` | Згенерувати або оновити XML підсистеми. |
| `subsystem-edit` | Редагувати склад і властивості підсистеми. |
| `subsystem-info` | Показати інформацію про підсистему та її обʼєкти. |
| `subsystem-validate` | Перевірити XML підсистеми. |
| `interface-edit` | Редагувати командний інтерфейс і повʼязані XML-елементи. |
| `interface-validate` | Перевірити структуру інтерфейсу. |
| `template-add` | Додати шаблон або повʼязаний допоміжний артефакт. |
| `template-remove` | Видалити шаблон і повʼязані посилання. |
| `help-add` | Додати довідку або help-артефакти до обʼєкта. |

### Web-публікація і тестування

| Skill | Призначення |
|---|---|
| `web-publish` | Опублікувати інформаційну базу або web-клієнт. |
| `web-unpublish` | Зняти web-публікацію. |
| `web-info` | Показати інформацію про web-публікацію. |
| `web-test` | Виконати smoke-тест або перевірку доступності web-клієнта. |
| `web-stop` | Зупинити web-сервіс або повʼязаний процес. |

### Візуальні та допоміжні tools

| Skill | Призначення |
|---|---|
| `img-grid` | Накласти сітку на зображення для аналізу форм, макетів і пропорцій. |

### UA-specific skills цього репозиторію

| Skill | Призначення |
|---|---|
| `ua-1c-platform-compat` | Визначити XML format, `CompatibilityMode`, rules `Configuration.xml` і режим валідації `GeneratedType` для українських конфігурацій. |
| `ua-configurationxml-features` | Перевіряти й пояснювати feature-елементи `Configuration.xml` для 8.3.16+, 8.3.17+, 8.3.18+, 8.3.20+ і 8.5.x. |

---

## 🛠 Команди build-системи

```bash
python build/apply.py build
```

Повна збірка: очистити тимчасову директорію, підготувати upstream, застосувати patches та overlays, згенерувати agent outputs, документацію і запустити validate.

```bash
python build/apply.py validate
```

Перевірити конфіги, registry платформ, наявність skills, agent outputs, hardcoded `.claude/skills`, resolver і GeneratedType rules.

```bash
python build/apply.py platform-info 8.3.20.1234
```

Показати нормалізовану версію платформи, XML format, `CompatibilityMode`, features `Configuration.xml` і режим `GeneratedType`.

```bash
python build/apply.py docs
```

Згенерувати `docs/PLATFORM_VERSIONS_UA.md` із YAML registry.

```bash
python build/apply.py update-upstream
```

Оновити upstream submodule і `upstream.lock`.

```bash
python build/apply.py apply-patches
python build/apply.py apply-overlays
python build/apply.py clean
```

Окремі службові команди для супроводу downstream-шару.

---

## 🔄 Оновлення upstream

Оновлення робиться контрольовано:

```bash
python build/apply.py update-upstream
python build/apply.py apply-patches
python build/apply.py build
python build/apply.py validate
python -m pytest
git status
```

Після перевірки:

```bash
git add .
git commit -m "Update upstream and reapply UA overlays"
git push
```

Якщо patch не застосовується:

1. відкрийте відповідний файл у `patches/`;
2. порівняйте зміни upstream у `upstream/cc-1c-skills`;
3. оновіть patch мінімально;
4. повторіть `python build/apply.py apply-patches`;
5. запустіть `build`, `validate`, `pytest`.

---

## ✅ Тести і CI

Локально:

```bash
python -m pytest
python build/apply.py validate
python build/apply.py build
```

GitHub Actions:

```text
.github/workflows/ci.yml
.github/workflows/upstream-check.yml
```

CI перевіряє:

- pytest;
- валідність YAML-конфігів;
- platform resolver;
- GeneratedType validation rules;
- agent outputs;
- build idempotency;
- можливість застосувати patches до upstream.

---

## 📚 Документація

| Файл | Зміст |
|---|---|
| `docs/ARCHITECTURE.md` | Архітектура шарів upstream → patches → overlays → configs → build → dist. |
| `docs/PLATFORM_VERSIONS_UA.md` | Згенерована документація з `configs/platform_versions_ua.yaml`. |
| `docs/UPSTREAM_SYNC.md` | Як оновлювати upstream і вирішувати patch-конфлікти. |
| `docs/AGENTS.md` | Як працюють ChatGPT, Claude, Codex, Gemini, Cursor adapters. |
| `docs/MIGRATION.md` | Міграція з оригінального `cc-1c-skills`. |

---

## 🤝 Як додати нову українську адаптацію

1. Оновіть `configs/platform_versions_ua.yaml` або додайте overlay у `overlays/`.
2. Якщо потрібна зміна upstream-файлу — створіть мінімальний patch у `patches/`.
3. Додайте або оновіть тест у `tests/`.
4. Згенеруйте документацію:

   ```bash
   python build/apply.py docs
   ```

5. Запустіть перевірки:

   ```bash
   python build/apply.py build
   python build/apply.py validate
   python -m pytest
   ```

---

## 🔐 Важливі правила супроводу

- Не редагуйте `upstream/cc-1c-skills` вручну як downstream-зміни.
- Усі українські відмінності зберігайте в `configs/`, `patches/`, `overlays/`, `docs/`, `tests/`.
- Не хардкодьте версії платформ у Python-коді — змінюйте YAML registry.
- Не привʼязуйте нові skills тільки до `.claude/skills` — використовуйте agent adapters.
- Після кожного оновлення upstream запускайте `build`, `validate`, `pytest`.

---

## 📄 Ліцензія

Цей репозиторій розповсюджується за ліцензією **MIT**. Дивіться файл [`LICENSE`](LICENSE).

Upstream [`Nikolay-Shirokov/cc-1c-skills`](https://github.com/Nikolay-Shirokov/cc-1c-skills) також використовується як базовий open-source компонент і підключається окремо як `upstream/cc-1c-skills`.

---

## Подяка upstream

Основний набір skills створено в межах upstream-проєкту [`Nikolay-Shirokov/cc-1c-skills`](https://github.com/Nikolay-Shirokov/cc-1c-skills). `uk-1c-skills` додає до нього український compatibility layer, підтримку BAF/BAS workflow, універсальні agent outputs і контрольований процес супроводу downstream-змін.
