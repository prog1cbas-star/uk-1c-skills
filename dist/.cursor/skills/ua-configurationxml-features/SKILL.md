---
name: ua-configurationxml-features
description: проверка и объяснение украинских правил Configuration.xml для платформ 1С 8.3.16+, 8.3.17+, 8.3.18+, 8.3.20+ и 8.5.x. использовать при валидации CF/CFE XML dumps и миграции конфигураций.
---

# UA Configuration.xml Features

Этот skill дополняет upstream skills `cf-*` и `cfe-*` UA-правилами из `configs/platform_versions_ua.yaml`.

## Проверка

```bash
python build/apply.py platform-info 8.3.20
```

Проверяй наличие feature-элементов только через registry:

- `StandaloneConfigurationRestrictionRoles` для `8.3.16+`;
- `InternalInfoContainedObject7` с `ClassId fb282519-d103-4dd3-bc12-cb271d631dfc` для `8.3.17+`;
- `URLExternalDataStorage` и `MobileApplicationURLs` для `8.3.18+`;
- `DefaultReportAppearanceTemplate`, `AllowedIncomingShareRequestTypes`, `DatabaseTablespacesUseMode` для `8.3.20+`.

Для non-Claude outputs build-система удаляет unsupported `allowed-tools` из frontmatter, а для Claude оставляет совместимость.
