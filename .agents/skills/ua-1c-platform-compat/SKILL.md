---
name: ua-1c-platform-compat
description: украинский compatibility layer для 1С:Предприятие 8.3/8.5. использовать, когда нужно определить XML format, CompatibilityMode, правила Configuration.xml или поведение GeneratedType validation для украинских конфигураций 1С.
---

# UA 1C Platform Compatibility

Используй registry `configs/platform_versions_ua.yaml` как источник истины. Не выводи правила версий из памяти и не добавляй новые условия вручную в Python-код.

## Быстрые команды

```bash
python build/apply.py platform-info 8.3.20
python build/apply.py platform-info 8.3.20.1234
python build/apply.py platform-info 8.5.1
```

## Правила работы

1. Нормализуй версию через resolver.
2. Возьми `xml_format`, `compatibility_mode`, `configuration_xml_features` и `generated_type_name_validation` из YAML.
3. Для `8.3.15`–`8.3.19` несовпадение `GeneratedType name` и `<Name>` считать ошибкой.
4. Для `8.3.20+` и `8.5.x` несовпадение считать предупреждением.
5. При изменении registry обнови `docs/PLATFORM_VERSIONS_UA.md` командой `python build/apply.py docs` и добавь тест.
