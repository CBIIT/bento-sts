import pytest

@pytest.mark.options(debug=False)
@pytest.skip(allow_module_level=True)
def test_app(app):
    assert not app.debug, 'Ensure the app not in debug mode'
