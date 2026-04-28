from uk1c.platforms import validate_generated_type_name


def test_generated_type_validation_strict_before_8_3_20():
    result = validate_generated_type_name("8.3.19", "CatalogObject.Wrong", "CatalogObject.Right")
    assert result["errors"]
    assert not result["warnings"]


def test_generated_type_validation_tolerant_from_8_3_20():
    result = validate_generated_type_name("8.3.20", "CatalogObject.Wrong", "CatalogObject.Right")
    assert not result["errors"]
    assert result["warnings"]
