import httpx
from icecream import ic


def test_get_existing_event(
    organisation, event, attribute, galaxy, galaxy_cluster, tag, site_admin_user_token, eventtag, client
) -> None:
    org_id = organisation.id

    event_id = event.id
    attribute_id = attribute.id
    galaxy_id = galaxy.id
    tag_id = tag.id

    galaxy_cluster_id = galaxy_cluster.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/events/{event_id}", headers=headers)

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

    legacy_response = httpx.get(f"http://misp-core/events/{event_id}", headers=headers)
    ic(legacy_response)
    assert False
