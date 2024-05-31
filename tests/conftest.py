import asyncio
import string
from contextlib import ExitStack
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from icecream import ic
from nanoid import generate
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from mmisp.api.auth import encode_token
from mmisp.api.main import init_app
from mmisp.db.config import config
from mmisp.db.database import Base
from mmisp.db.models.event import EventTag
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.db.models.sharing_group import SharingGroupOrg, SharingGroupServer
from mmisp.util.crypto import hash_secret
from tests.generators.model_generators.auth_key_generator import generate_auth_key
from tests.generators.model_generators.server_generator import generate_server

from .generators.model_generators.attribute_generator import generate_attribute
from .generators.model_generators.event_generator import generate_event
from .generators.model_generators.galaxy_generator import generate_galaxy
from .generators.model_generators.organisation_generator import generate_organisation
from .generators.model_generators.role_generator import generate_org_admin_role, generate_site_admin_role
from .generators.model_generators.sharing_group_generator import generate_sharing_group
from .generators.model_generators.tag_generator import generate_tag
from .generators.model_generators.user_generator import generate_user


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def connection(event_loop):
    url = make_url(config.DATABASE_URL)

    if "mysql" in url.drivername:
        url = url.set(drivername="mysql+mysqlconnector")
    if "sqlite" in url.drivername:
        url = url.set(drivername="sqlite")

    print(url)

    engine = create_engine(url, echo=True)
    #    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


@pytest.fixture(scope="function")
def db(connection) -> Generator[Session, None, None]:
    with connection() as db:
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
def instance_org_two_admin_user_token(instance_org_two_admin_user):
    return encode_token(instance_org_two_admin_user.id)


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
def event(db, organisation, site_admin_user):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = site_admin_user.id

    db.add(event)
    db.commit()
    db.refresh(event)

    yield event

    db.delete(event)
    db.commit()


@pytest.fixture
def event2(db, organisation, site_admin_user):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = site_admin_user.id

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
    event.attribute_count += 1

    db.add(attribute)
    db.commit()
    db.refresh(attribute)

    yield attribute

    db.delete(attribute)
    event.attribute_count -= 1
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
    tag.exportable = True

    db.add(tag)
    db.commit()
    db.refresh(tag)

    yield tag

    db.delete(tag)
    db.commit()


@pytest.fixture
def sharing_group(db, instance_owner_org):
    sharing_group = generate_sharing_group()
    sharing_group.organisation_uuid = instance_owner_org.uuid
    sharing_group.org_id = instance_owner_org.id

    db.add(sharing_group)
    db.commit()
    db.refresh(sharing_group)

    yield sharing_group

    db.delete(sharing_group)
    db.commit()


@pytest.fixture
def sharing_group2(db, instance_org_two):
    sharing_group = generate_sharing_group()
    sharing_group.organisation_uuid = instance_org_two.uuid
    sharing_group.org_id = instance_org_two.id

    db.add(sharing_group)
    db.commit()
    db.refresh(sharing_group)

    yield sharing_group

    db.delete(sharing_group)
    db.commit()


@pytest.fixture
def sharing_group_org(db, sharing_group, instance_owner_org):
    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=instance_owner_org.id)
    db.add(sharing_group_org)
    db.commit()
    yield sharing_group_org
    db.delete(sharing_group_org)
    db.commit()


@pytest.fixture
def sharing_group_org_two(db, sharing_group, instance_org_two):
    ic(instance_org_two)
    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=instance_org_two.id)
    db.add(sharing_group_org)
    db.commit()
    yield sharing_group_org
    db.delete(sharing_group_org)
    db.commit()


@pytest.fixture
def server(db, instance_owner_org):
    server = generate_server()
    server.org_id = instance_owner_org.id

    db.add(server)
    db.commit()
    yield server

    db.delete(server)
    db.commit()


@pytest.fixture
def sharing_group_server(db, sharing_group, server):
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=server.id)

    db.add(sharing_group_server)
    db.commit()

    yield sharing_group_server

    db.delete(sharing_group_server)
    db.commit()


@pytest.fixture
def sharing_group_server_all_orgs(db, server, sharing_group):
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=server.id, all_orgs=True)

    db.add(sharing_group_server)
    db.commit()

    yield sharing_group_server

    db.delete(sharing_group_server)
    db.commit()


@pytest.fixture
def galaxy(db):
    galaxy = generate_galaxy()

    db.add(galaxy)
    db.commit()
    db.refresh(galaxy)

    yield galaxy

    db.delete(galaxy)
    db.commit()


@pytest.fixture
def galaxy_cluster(db, tag, galaxy):
    galaxy_cluster = GalaxyCluster(
        collection_uuid="uuid",
        type="test type",
        value="test",
        tag_name=tag.name,
        description="test",
        galaxy_id=galaxy.id,
        authors="admin",
    )

    db.add(galaxy_cluster)
    db.commit()
    db.refresh(galaxy_cluster)

    yield galaxy_cluster

    db.delete(galaxy_cluster)
    db.commit()


@pytest.fixture
def eventtag(db, event, tag):
    eventtag = EventTag(event_id=event.id, tag_id=tag.id, local=False)

    db.add(eventtag)
    db.commit()
    db.refresh(eventtag)

    yield eventtag

    db.delete(eventtag)
    db.commit()


@pytest.fixture()
def auth_key(db, site_admin_user):
    clear_key = generate(string.ascii_letters + string.digits, size=40)

    auth_key = generate_auth_key()
    auth_key.user_id = site_admin_user.id
    auth_key.authkey = hash_secret(clear_key)
    auth_key.authkey_start = clear_key[:4]
    auth_key.authkey_end = clear_key[-4:]

    db.add(auth_key)

    db.commit()
    db.refresh(auth_key)

    yield clear_key, auth_key

    db.delete(auth_key)
    db.commit()
