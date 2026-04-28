from uk1c.platforms import PlatformResolver


def test_platform_resolver_required_versions():
    resolver = PlatformResolver.from_file()
    cases = {
        "8.3.15": ("8.3.15", "2.9", "Version8_3_15"),
        "8.3.20": ("8.3.20", "2.13", "Version8_3_20"),
        "8.3.20.1234": ("8.3.20", "2.13", "Version8_3_20"),
        "8.3.27": ("8.3.27", "2.20", "Version8_3_27"),
        "8.3.27.1500": ("8.3.27", "2.20", "Version8_3_27"),
        "8.5.x": ("8.5.x", "2.21", "Version8_5_X"),
        "8.5.1": ("8.5.x", "2.21", "Version8_5_X"),
    }
    for raw, expected in cases.items():
        resolved = resolver.resolve(raw)
        assert (resolved.key, resolved.xml_format, resolved.compatibility_mode) == expected
