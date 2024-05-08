from typing import Generator

import pytest
from sqlalchemy.orm import Session

from mmisp.api.auth import encode_token
from tests.database import get_db
from tests.generators.model_generators.server_generator import generate_server

from .generators.model_generators.attribute_generator import generate_attribute
from .generators.model_generators.event_generator import generate_event
from .generators.model_generators.organisation_generator import generate_organisation
from .generators.model_generators.role_generator import generate_org_admin_role, generate_site_admin_role
from .generators.model_generators.tag_generator import generate_tag
from .generators.model_generators.user_generator import generate_user
from .generators.model_generators.sharing_group_generator import generate_sharing_group


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    with get_db() as db:
        yield db


@pytest.fixture
def site_admin_role(db):
    role = generate_site_admin_role()
    db.add(role)
    db.commit()
    yield role
    db.delete(role)
    db.commit()


@pytest.fixture
def org_admin_role(db):
    role = generate_org_admin_role()
    db.add(role)
    db.commit()
    yield role
    db.delete(role)
    db.commit()


@pytest.fixture
def instance_owner_org(db):
    instance_owner_org = generate_organisation()
    db.add(instance_owner_org)
    db.commit()
    yield instance_owner_org
    db.delete(instance_owner_org)
    db.commit()


@pytest.fixture
def instance_org_two(db):
    org = generate_organisation()
    db.add(org)
    db.commit()
    yield org
    db.delete(org)
    db.commit()


@pytest.fixture
def instance_two_owner_org(db):
    org = generate_organisation()
    org.local = False
    db.add(org)
    db.commit()
    yield org
    db.delete(org)
    db.commit()


@pytest.fixture
def site_admin_user(db, site_admin_role, instance_owner_org):
    user = generate_user()
    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = site_admin_role.id

    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def instance_owner_org_admin_user(db, instance_owner_org, org_admin_role):
    user = generate_user()
    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = org_admin_role.id

    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def instance_two_server(db, instance_two_owner_org):
    server = generate_server()
    server.name = "Instance Two Server"
    server.org_id = instance_two_owner_org.id
    server.url = "http://instance-two.mmisp.service"

    db.add(server)
    db.commit()
    yield server
    db.delete(server)
    db.commit()


@pytest.fixture
def instance_org_two_admin_user(db, instance_org_two, org_admin_role):
    user = generate_user()
    user.org_id = instance_org_two.id
    user.server_id = 0
    user.role_id = org_admin_role.id

    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def instance_two_owner_org_admin_user(db, instance_two_owner_org, instance_two_server, org_admin_role):
    user = generate_user()
    user.org_id = instance_two_owner_org.id
    user.server_id = instance_two_server.id
    user.role_id = org_admin_role.id

    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def site_admin_user_token(site_admin_user):
    return encode_token(site_admin_user.id)


@pytest.fixture
def instance_owner_org_admin_user_token(instance_owner_org_admin_user):
    return encode_token(instance_owner_org_admin_user.id)


@pytest.fixture
def organisation(db):
    organisation = generate_organisation()

    db.add(organisation)
    db.commit()
    db.refresh(organisation)

    yield organisation

    db.delete(organisation)
    db.commit()


@pytest.fixture
def event(db, organisation):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id

    db.add(event)
    db.commit()
    db.refresh(event)

    yield event

    db.delete(event)
    db.commit()


@pytest.fixture
def event2(db, organisation):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id

    db.add(event)
    db.commit()
    db.refresh(event)

    yield event

    db.delete(event)
    db.commit()


@pytest.fixture
def attribute(db, event):
    event_id = event.id
    attribute = generate_attribute(event_id)

    db.add(attribute)
    db.commit()
    db.refresh(attribute)

    yield attribute

    db.delete(attribute)
    db.commit()


@pytest.fixture
def attribute2(db, event):
    event_id = event.id
    attribute = generate_attribute(event_id)

    db.add(attribute)
    db.commit()
    db.refresh(attribute)

    yield attribute

    db.delete(attribute)
    db.commit()


@pytest.fixture
def tag(db):
    tag = generate_tag()

    tag.user_id = 1
    tag.org_id = 1
    tag.is_galaxy = True

    db.add(tag)
    db.commit()
    db.refresh(tag)

    yield tag

    db.delete(tag)
    db.commit()

@pytest.fixture
def sharing_group(db, instance_org_two):
    sharing_group = generate_sharing_group()
    sharing_group.organisation_uuid = instance_org_two.uuid
    sharing_group.org_id = instance_org_two.id

    db.add(sharing_group)
    db.commit()
    db.refresh(sharing_group)

    yield sharing_group

    db.delete(sharing_group)
    db.commit()


