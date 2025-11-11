import pytest


@pytest.fixture(scope="function", autouse=True)
def _auto_prov_db(provision_db):
    """Auto provision the test database."""
    pass
