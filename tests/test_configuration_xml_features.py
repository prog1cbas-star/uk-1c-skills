from uk1c.platforms import PlatformResolver


def features(version: str) -> set[str]:
    return set(PlatformResolver.from_file().resolve(version).configuration_xml_features)


def test_configuration_xml_feature_thresholds():
    assert not features("8.3.15")
    assert "StandaloneConfigurationRestrictionRoles" in features("8.3.16")
    assert "InternalInfoContainedObject7" in features("8.3.17")
    assert {"URLExternalDataStorage", "MobileApplicationURLs"}.issubset(features("8.3.18"))
    assert {
        "DefaultReportAppearanceTemplate",
        "AllowedIncomingShareRequestTypes",
        "DatabaseTablespacesUseMode",
    }.issubset(features("8.3.20"))
