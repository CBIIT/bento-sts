import pytest
from app import create_app as app


@pytest.mark.options(debug=False)
def test_hello(app):
    response = app.test_client().get('/')

    assert response.status_code == 302
