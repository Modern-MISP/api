import httpx
import sqlalchemy as sa
from deepdiff import DeepDiff
from icecream import ic


def test_get_existing_event(
    db, organisation, event, attribute, galaxy, galaxy_cluster, tag, auth_key, eventtag, client
) -> None:
    clear_key, auth_key = auth_key
    org_id = organisation.id

    event_id = event.id
    attribute_id = attribute.id
    galaxy_id = galaxy.id
    tag_id = tag.id

    galaxy_cluster_id = galaxy_cluster.id

    headers = {"authorization": clear_key, "accept": "application/json"}
    response = client.get(f"/events/view/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["id"] == str(event_id)
    assert response_json["Event"]["org_id"] == str(org_id)
    assert response_json["Event"]["orgc_id"] == str(org_id)
    assert response_json["Event"]["attribute_count"] == "1"
    assert response_json["Event"]["Attribute"][0]["id"] == str(attribute_id)
    assert response_json["Event"]["Tag"][0]["id"] == str(tag_id)
    assert response_json["Event"]["Galaxy"][0]["id"] == str(galaxy_id)
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["id"] == str(galaxy_cluster_id)
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["event_tag_id"] == str(eventtag.id)

    # do not remove this its needed for gitlab-ci. why? i do not know
    db.commit()
    #    stmt = sa.sql.text("SELECT * FROM users")
    #    for row in db.execute(stmt, {}):
    #        print(row)
    #    stmt = sa.sql.text("SELECT * FROM auth_keys")
    #    for row in db.execute(stmt, {}):
    #        print(row)
    # time.sleep(5)

    legacy_response = httpx.get(f"http://misp-core/events/view/{event_id}?extended=true", headers=headers)
    ic(legacy_response.text)
    ic(legacy_response.headers)
    db.commit()
    stmt = sa.sql.text("SELECT * FROM logs ORDER BY id DESC LIMIT 5")
    for row in db.execute(stmt, {}):
        print(row)
    assert DeepDiff(response_json, legacy_response.json()) == {}
