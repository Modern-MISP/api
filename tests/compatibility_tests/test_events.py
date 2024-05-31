import httpx
from deepdiff import DeepDiff
from icecream import ic


def to_legacy_format(data):
    if isinstance(data, bool):
        return data
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, dict):
        return {key: to_legacy_format(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [to_legacy_format(x) for x in data]
    return data


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

    ic(response_json)

    assert response_json["Event"]["id"] == str(event_id)
    assert response_json["Event"]["org_id"] == str(org_id)
    assert response_json["Event"]["orgc_id"] == str(org_id)
    assert response_json["Event"]["attribute_count"] == "1"
    assert response_json["Event"]["Attribute"][0]["id"] == str(attribute_id)
    assert response_json["Event"]["Tag"][0]["id"] == str(tag_id)
    assert response_json["Event"]["Galaxy"][0]["id"] == str(galaxy_id)
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["id"] == str(galaxy_cluster_id)
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["event_tag_id"] == str(eventtag.id)

    db.commit()

    # TODO: fix this
    for attr in response_json["Event"]["Attribute"]:
        attr.pop("Tag")
    response_json["Event"].pop("Galaxy")
    response_json_in_legacy = to_legacy_format(response_json)

    legacy_response = httpx.get(f"http://misp-core/events/view/{event_id}?extended=true", headers=headers)
    legacy_response_json = legacy_response.json()
    legacy_response_json["Event"].pop("Galaxy")

    ic(response_json_in_legacy)
    ic(legacy_response_json)
    db.commit()
    assert DeepDiff(response_json_in_legacy, legacy_response_json) == {}
