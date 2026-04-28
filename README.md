# uk-1c-skills

`uk-1c-skills` — поддерживаемый downstream-репозиторий для украинской адаптации AI-agent skills разработки на платформе 1С:Предприятие 8.3/8.5.

Репозиторий рассчитан на работу поверх upstream `Nikolay-Shirokov/cc-1c-skills` без ручного редактирования upstream-файлов. Базовая стратегия: upstream как git submodule, затем reproducible build через `patches/`, `overlays/`, `configs/` и Python build-систему.

## Чем отличается от upstream

Upstream `cc-1c-skills` хранит основные skills в `.claude/skills/` и уже содержит `scripts/switch.py` для разных AI-платформ. Этот downstream добавляет слой сопровождения:

- UA registry платформ 1С в `configs/platform_versions_ua.yaml`;
- resolver версий `8.3.20.1234 -> 8.3.20`, `8.5.1 -> 8.5.x`;
- patch/overlay-based workflow без прямых правок upstream;
- генерацию outputs для `.agents`, `.claude`, `.codex`, `.gemini`, `.cursor`;
- тесты, CI и документацию для сопровождения.

## Быстрый старт

```bash
git clone https://github.com/elftorgcom/uk-1c-skills.git
cd uk-1c-skills

# если submodule ещё не добавлен в вашем git-репозитории
git submodule add https://github.com/Nikolay-Shirokov/cc-1c-skills.git upstream/cc-1c-skills || true
git submodule update --init --recursive

python -m pip install -e . pytest PyYAML
python build/apply.py build
python build/apply.py validate
python -m pytest
```

Если upstream submodule не инициализирован, build-система не редактирует upstream и не падает: она использует локальные UA skills из `.agents/skills` и `overlays/skills`, чтобы репозиторий оставался проверяемым офлайн. При наличии `upstream/cc-1c-skills/.claude/skills` будут сгенерированы outputs и для upstream skills.

## Использование с AI-агентами

После сборки готовые skills лежат в `dist/`:

```text
dist/.agents/skills/   # ChatGPT / универсальный Agent Skills layout
dist/.claude/skills/   # Claude Code compatible layout
dist/.codex/skills/    # OpenAI Codex layout
dist/.gemini/skills/   # Gemini CLI layout
dist/.cursor/skills/   # Cursor layout
```

Скопируйте нужный каталог в проект или используйте его как artifact CI.

## Основные команды

```bash
python build/apply.py build
python build/apply.py validate
python build/apply.py platform-info 8.3.20
python build/apply.py docs
python build/apply.py update-upstream
python build/apply.py apply-patches
python build/apply.py apply-overlays
python build/apply.py clean
```

Пример resolver:

```bash
python build/apply.py platform-info 8.3.20.1234
```

## UA-адаптации платформ

Registry платформ находится в `configs/platform_versions_ua.yaml`. Python-код читает правила оттуда, а не содержит длинные hardcoded `if/else` по версиям.

Сейчас registry описывает:

- XML format и `CompatibilityMode` для 8.3.15–8.3.27 и 8.5.x;
- изменения `Configuration.xml` начиная с 8.3.16, 8.3.17, 8.3.18, 8.3.20;
- разные правила валидации `GeneratedType`: strict для 8.3.15–8.3.19 и tolerant для 8.3.20+.

## Почему submodule, а не subtree

По умолчанию используется submodule: upstream остаётся чистым, его commit можно зафиксировать в `upstream.lock`, а downstream-изменения живут отдельно. Subtree можно рассмотреть позже, если нужен полностью self-contained monorepo без submodule workflow, но тогда повышается риск смешать upstream и UA изменения.

Подробнее см. `docs/ARCHITECTURE.md`, `docs/UPSTREAM_SYNC.md`, `docs/AGENTS.md`, `docs/MIGRATION.md`.
