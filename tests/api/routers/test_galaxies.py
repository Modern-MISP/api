from typing import Any

import pytest
from sqlalchemy.orm import Session

from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody

from ...environment import client, environment, get_db
from ...generators.galaxy_generator import generate_valid_import_galaxy_cluster_body


@pytest.fixture(scope="function")
def db() -> Session:
    db_session = get_db()

    yield db_session

    db_session.close()


@pytest.fixture(scope="module")
def import_galaxy_cluster_valid_data() -> list[Any]:
    return generate_valid_import_galaxy_cluster_body()


class TestImportGalaxyCluster:
    def test_import_galaxy_cluster_valid_data(
        self: "TestImportGalaxyCluster", import_galaxy_cluster_valid_data: list[ImportGalaxyBody]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/import", json=import_galaxy_cluster_valid_data, headers=headers)
        response_json = response.json()
        print(response_json)
        assert response.status_code == 200
        assert response_json["saved"] is True
        assert response_json["success"] is True
        assert response_json["name"] == "Galaxy clusters imported. 1 imported, 0 ignored, 0 failed."

    # def test_import_galaxy_cluster_invalid_data(self: "TestImportGalaxyCluster") -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post("/galaxies/import", json={}, headers=headers)
    #
    #     assert response.status_code == 500
