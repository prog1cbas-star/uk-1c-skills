# UA registry версий платформ 1С

Файл сгенерирован из `configs/platform_versions_ua.yaml` командой `python build/apply.py docs`.

## Версии

| Платформа | XML format | CompatibilityMode | GeneratedType | Configuration.xml features |
|---|---:|---|---|---|
| `8.3.15` | `2.9` | `Version8_3_15` | `strict` | — |
| `8.3.16` | `2.9.1` | `Version8_3_16` | `strict` | StandaloneConfigurationRestrictionRoles |
| `8.3.17` | `2.10` | `Version8_3_17` | `strict` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7 |
| `8.3.18` | `2.11` | `Version8_3_18` | `strict` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs |
| `8.3.19` | `2.12` | `Version8_3_19` | `strict` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs |
| `8.3.20` | `2.13` | `Version8_3_20` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.21` | `2.14` | `Version8_3_21` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.22` | `2.15` | `Version8_3_22` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.23` | `2.16` | `Version8_3_23` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.24` | `2.17` | `Version8_3_24` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.25` | `2.18` | `Version8_3_25` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.26` | `2.19` | `Version8_3_26` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.3.27` | `2.20` | `Version8_3_27` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |
| `8.5.x` | `2.21` | `Version8_5_X` | `tolerant` | StandaloneConfigurationRestrictionRoles, InternalInfoContainedObject7, URLExternalDataStorage, MobileApplicationURLs, DefaultReportAppearanceTemplate, AllowedIncomingShareRequestTypes, DatabaseTablespacesUseMode |

## Configuration.xml features

### StandaloneConfigurationRestrictionRoles

- Introduced in: `8.3.16`
- XML: `<StandaloneConfigurationRestrictionRoles/>`
- Description: Роли ограничения автономной конфигурации

### InternalInfoContainedObject7

- Introduced in: `8.3.17`
- XML: `7-й xr:ContainedObject в InternalInfo`
- ClassId: `fb282519-d103-4dd3-bc12-cb271d631dfc`
- Description: Дополнительный contained object в InternalInfo

### URLExternalDataStorage

- Introduced in: `8.3.18`
- XML: `<URLExternalDataStorage/>`
- Description: URL внешнего хранилища данных

### MobileApplicationURLs

- Introduced in: `8.3.18`
- XML: `<MobileApplicationURLs/>`
- Description: URL мобильных приложений

### DefaultReportAppearanceTemplate

- Introduced in: `8.3.20`
- XML: `<DefaultReportAppearanceTemplate/>`
- Description: Шаблон оформления отчётов по умолчанию

### AllowedIncomingShareRequestTypes

- Introduced in: `8.3.20`
- XML: `<AllowedIncomingShareRequestTypes/>`
- Description: Разрешённые типы входящих share-запросов

### DatabaseTablespacesUseMode

- Introduced in: `8.3.20`
- XML: `<DatabaseTablespacesUseMode>DontUse</DatabaseTablespacesUseMode>`
- Description: Режим использования tablespaces базы данных

## GeneratedType validation

- `8.3.15`–`8.3.19`: strict, mismatch is error.
- `8.3.20+` и `8.5.x`: tolerant, mismatch is warning.

Правила берутся из YAML registry; Python resolver не содержит длинных version-specific `if/else`.
