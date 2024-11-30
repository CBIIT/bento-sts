import pytest

@pytest.mark.options(debug=False)
@pytest.skip(allow_module_level=True)
def test_hello(app):
    response = app.test_client().get('/')

    assert response.status_code == 302
