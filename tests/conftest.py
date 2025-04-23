import atexit
import logging
import random
import string
import uuid as libuuid
from contextlib import AsyncExitStack, ExitStack
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Self, Tuple

import pytest
import pytest_asyncio
from _pytest.config import create_terminal_writer
from fastapi.testclient import TestClient
from icecream import ic
from pytest import Config, Item, hookimpl
from sqlalchemy.ext.asyncio import AsyncSession

import mmisp.lib.standard_roles as standard_roles
import mmisp.util.crypto
from mmisp.api.auth import encode_token
from mmisp.api.main import init_app
from mmisp.db.models.admin_setting import AdminSetting
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.auth_key import AuthKey
from mmisp.db.models.event import EventTag
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.db.models.user import User
from mmisp.db.models.workflow import Workflow
from mmisp.lib.attributes import AttributeCategories
from mmisp.lib.distribution import AttributeDistributionLevels, EventDistributionLevels
from mmisp.tests.fixtures import *  # noqa
from mmisp.tests.generators.model_generators.attribute_generator import generate_attribute
from mmisp.tests.generators.model_generators.tag_generator import generate_tag
from mmisp.tests.generators.model_generators.user_generator import generate_user
from mmisp.tests.generators.model_generators.user_setting_generator import generate_user_name
from mmisp.util.crypto import hash_secret
from mmisp.workflows.graph import Apperance, WorkflowGraph
from mmisp.workflows.input import WorkflowInput
from mmisp.workflows.modules import (
    ModuleAction,
    ModuleConfiguration,
    ModuleStopExecution,
    TriggerEventBeforeSave,
    TriggerEventPublish,
    workflow_node,
)


def pytest_addoption(parser):
    group = parser.getgroup("split your tests into groups and run them")
    group.addoption(
        "--test-group-count", dest="test-group-count", type=int, help="The number of groups to split the tests into"
    )
    group.addoption("--test-group", dest="test-group", type=int, help="The group of tests that should be executed")


@hookimpl(trylast=True)
def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    group_count: int = config.getoption("test-group-count")  # type: ignore
    group_id: int = config.getoption("test-group")  # type: ignore

    if not group_count or not group_id:
        return

    items.sort(key=lambda x: x.nodeid)

    start = group_id - 1
    items[:] = items[start::group_count]

    terminal_reporter = config.pluginmanager.get_plugin("terminalreporter")
    terminal_writer = create_terminal_writer(config)
    message = terminal_writer.markup("Running test group #{0} ({1} tests)\n".format(group_id, len(items)), yellow=True)
    terminal_reporter.write(message)


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        app = init_app()
        logging.getLogger("mmisp").addHandler(logging.StreamHandler())
        yield app


@pytest_asyncio.fixture
async def sharing_group_org_two(db, sharing_group, instance_org_two):
    ic(instance_org_two)
    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=instance_org_two.id)
    db.add(sharing_group_org)
    await db.commit()
    yield sharing_group_org
    await db.delete(sharing_group_org)
    await db.commit()


@pytest_asyncio.fixture
async def sharing_group_server_all_orgs(db, server, sharing_group):
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=server.id, all_orgs=True)

    db.add(sharing_group_server)
    await db.commit()

    yield sharing_group_server

    await db.delete(sharing_group_server)
    await db.commit()


@pytest_asyncio.fixture
async def sharing_group_server(db, sharing_group, server):
    sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=server.id)

    db.add(sharing_group_server)
    await db.commit()

    yield sharing_group_server

    await db.delete(sharing_group_server)
    await db.commit()


@pytest_asyncio.fixture
async def event3(db, organisation, site_admin_user):
    org_id = organisation.id
    event = Event(
        org_id=org_id,
        orgc_id=org_id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="test event",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.ALL_COMMUNITIES,
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def event4(db, organisation, site_admin_user):
    org_id = organisation.id
    event = Event(
        org_id=org_id,
        orgc_id=org_id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="test event",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.ALL_COMMUNITIES,
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def event5(db, organisation, site_admin_user):
    org_id = organisation.id
    event = Event(
        org_id=org_id,
        orgc_id=org_id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="test event",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.ALL_COMMUNITIES,
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest.fixture
async def attribute3(db, event):
    event_id = event.id
    attribute = generate_attribute(event_id)
    event.attribute_count += 1

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(attribute)
    event.attribute_count -= 1
    await db.commit()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def site_admin_user_token(site_admin_user):
    return encode_token(site_admin_user.id)


@pytest.fixture
def instance_owner_org_admin_user_token(instance_owner_org_admin_user):
    return encode_token(instance_owner_org_admin_user.id)


@pytest.fixture
def instance_org_two_admin_user_token(instance_org_two_admin_user):
    return encode_token(instance_org_two_admin_user.id)


@pytest_asyncio.fixture
async def eventtag(db, event, tag):
    eventtag = EventTag(event_id=event.id, tag_id=tag.id, local=False)

    db.add(eventtag)
    await db.commit()
    await db.refresh(eventtag)

    yield eventtag

    await db.delete(eventtag)
    await db.commit()


@pytest_asyncio.fixture
async def galaxy_cluster(db, tag, galaxy):
    galaxy_cluster = GalaxyCluster(
        collection_uuid="da4b7a8d-d314-42e8-9c85-2eb476e90dbf",
        type="test type",
        value="test",
        tag_name=tag.name,
        description="test",
        galaxy_id=galaxy.id,
        authors=["admin"],
    )

    db.add(galaxy_cluster)
    await db.commit()
    await db.refresh(galaxy_cluster)

    yield galaxy_cluster

    await db.delete(galaxy_cluster)
    await db.commit()


@pytest_asyncio.fixture
async def view_only_user(db, user_role, instance_owner_org):
    user = generate_user()
    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = user_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    db.add(user_setting)
    await db.commit()

    yield user
    await db.delete(user_setting)
    await db.commit()
    await db.delete(user)
    await db.commit()


@pytest.fixture
def read_only_user_token(view_only_user):
    return encode_token(view_only_user.id)


@pytest_asyncio.fixture
async def blocking_publish_workflow(db):
    setting = AdminSetting(setting="workflow_feature_enabled", value="True")
    db.add(setting)
    trigger = TriggerEventPublish(
        graph_id=1,
        inputs={},
        outputs={1: []},
        apperance=Apperance((0, 0), False, "", None),
    )
    publish = ModuleStopExecution(
        inputs={1: [(1, trigger)]},
        graph_id=2,
        outputs={},
        apperance=Apperance((0, 0), False, "", None),
        on_demand_filter=None,
        configuration=ModuleConfiguration({"message": "Stopped publish of {{Event.info}}"}),
    )
    trigger.outputs[1].append((1, publish))

    wf = Workflow(
        id=1,
        uuid=str(uuid()),
        name="Demo workflow",
        description="",
        timestamp=0,
        enabled=True,
        trigger_id=trigger.id,
        debug_enabled=True,
        data=WorkflowGraph(
            nodes={1: trigger, 2: publish},
            root=trigger,
            frames=[],
        ),
    )
    db.add(wf)
    await db.commit()
    yield wf
    await db.delete(wf)
    await db.delete(setting)
    await db.commit()


@pytest_asyncio.fixture
async def unsupported_workflow(db):
    setting = AdminSetting(setting="workflow_feature_enabled", value="True")
    db.add(setting)
    trigger = TriggerEventPublish(
        graph_id=1,
        inputs={},
        outputs={1: []},
        apperance=Apperance((0, 0), False, "", None),
    )

    @dataclass
    @workflow_node
    class MockupModule(ModuleAction):
        id: str = "demo"
        name: str = "Demo :: Dumb Module"
        description: str = "..."
        icon: str = "none"
        supported: bool = False

        async def exec(self: Self, payload: WorkflowInput, db: AsyncSession) -> Tuple[bool, Self | None]:
            return True, None

    module = MockupModule(
        graph_id=2,
        inputs={0: [(0, trigger)]},
        outputs={},
        configuration=ModuleConfiguration({}),
        on_demand_filter=None,
        apperance=Apperance((0, 0), False, "mock", None),
    )
    trigger.outputs[1].append((1, module))

    wf = Workflow(
        id=1,
        uuid=str(uuid()),
        name="Demo workflow",
        description="",
        timestamp=0,
        enabled=True,
        trigger_id=trigger.id,
        debug_enabled=False,
        data=WorkflowGraph(
            nodes={1: trigger, 2: module},
            root=trigger,
            frames=[],
        ),
    )
    db.add(wf)
    await db.commit()
    yield wf
    await db.delete(wf)
    await db.delete(setting)
    await db.commit()


@pytest_asyncio.fixture
async def failing_before_save_workflow(db):
    setting = AdminSetting(setting="workflow_feature_enabled", value="True")
    db.add(setting)
    trigger = TriggerEventBeforeSave(
        graph_id=1,
        inputs={},
        outputs={1: []},
        apperance=Apperance((0, 0), False, "", None),
    )
    stop = ModuleStopExecution(
        inputs={1: [(1, trigger)]},
        graph_id=2,
        outputs={},
        apperance=Apperance((0, 0), False, "", None),
        on_demand_filter=None,
        configuration=ModuleConfiguration({"message": "Stopped publish of {{Event.info}}"}),
    )
    trigger.outputs[1].append((1, stop))

    wf = Workflow(
        id=1,
        uuid=str(uuid()),
        name="Before save workflow",
        description="",
        timestamp=0,
        enabled=True,
        trigger_id=trigger.id,
        debug_enabled=True,
        data=WorkflowGraph(
            nodes={1: trigger, 2: stop},
            root=trigger,
            frames=[],
        ),
    )
    db.add(wf)
    await db.commit()
    yield wf
    await db.delete(wf)
    await db.delete(setting)
    await db.commit()


@pytest_asyncio.fixture
async def test_standard_role(db):
    role = standard_roles.sync_user_role()

    db.add(role)
    await db.commit()
    await db.refresh(role)

    yield role

    await db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def role_read_only(db):
    role = standard_roles.read_only_role()
    db.add(role)
    await db.commit()
    await db.refresh(role)

    yield role

    await db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def random_test_role(db):
    role = Role(
        id=42,
        name="test_role",
        perm_add=False,
        perm_modify=False,
        perm_modify_org=False,
        perm_publish=False,
        perm_delegate=False,
        perm_sync=False,
        perm_admin=False,
        perm_audit=False,
        perm_auth=False,
        perm_site_admin=False,
        perm_regexp_access=False,
        perm_tagger=False,
        perm_template=False,
        perm_sharing_group=False,
        perm_tag_editor=False,
        perm_sighting=False,
        perm_object_template=False,
        default_role=False,
        memory_limit="",
        max_execution_time="",
        restricted_to_site_admin=False,
        perm_publish_zmq=False,
        perm_publish_kafka=False,
        perm_decaying=False,
        enforce_rate_limit=False,
        rate_limit_count=0,
        perm_galaxy_editor=False,
        perm_warninglist=False,
        perm_view_feed_correlations=False,
        created=datetime.now(timezone.utc),
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    yield role

    await db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def random_test_user(db, instance_owner_org):
    user = User(
        password="very_safe_passwort",
        org_id=instance_owner_org.id,
        role_id=42,
        email="test_user@lauch.com",
        authkey=None,
        invited_by=314,
        nids_sid=0,
        termsaccepted=True,
        change_pw=True,
        contactalert=False,
        disabled=False,
        notification_daily=False,
        notification_weekly=False,
        notification_monthly=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    yield user

    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def access_test_objects(db, site_admin_user, site_admin_role, auth_key):
    """
    This is a massive fixture to provide scenarios to test access control.

    Nomenclature:
        - orgs are numbered org1, org2, ...
        - roles are named according to their db name
        - users have the pattern start with `user_<org>_<role>`, e.g. user_org1_modify
        - auth_keys and similar are the user attributes suffixed with _auth_key, _clear_key and _token
        - events have the pattern `event_<org>_<distributionlevel>_<published/unpublished>`
        - attributes have the pattern `attribute_<org>_<eventdistributionlevel>_<attributedistributionlevel>`
        - if the distributionlevel is sharing_group the sharing group is appended.
        - sharing groups have the pattern `sg_<org1>_<org2>`
    """
    instance_id = f"{''.join(random.choices(string.ascii_letters, k=15))}"

    site_admin_user_clear_key, site_admin_user_auth_key = auth_key

    def generate_auth_key(clear_key, user_id) -> AuthKey:
        return AuthKey(
            authkey=hash_secret(clear_key),
            authkey_start=clear_key[:4],
            authkey_end=clear_key[-4:],
            comment="test comment",
            user_id=user_id,
        )

    def generate_user(org, role) -> User:
        return User(
            password="very_safe_passwort",
            org_id=org.id,
            role_id=role.id,
            email=f"{instance_id}_{org.name}{role.name}@example.com",
            authkey=None,
            invited_by=314,
            nids_sid=0,
            termsaccepted=True,
            change_pw=False,
            contactalert=False,
            disabled=False,
            notification_daily=False,
            notification_weekly=False,
            notification_monthly=False,
        )

    def generate_organisation(id) -> Organisation:
        return Organisation(
            name=f"{instance_id}_{id}",
            uuid=libuuid.uuid4(),
            description=f"{instance_id}_{id}",
            type=f"{instance_id}_{id}",
            nationality="earthian",
            sector="software",
            created_by=0,
            contacts="Test Org",
            local=True,
            restricted_to_domain=[],
            landingpage="",
        )

    def generate_sharing_group(org1, org2) -> SharingGroup:
        return SharingGroup(
            name=f"{libuuid.uuid4().hex}",
            description=f"sg_{org1.name}_{org2.name}",
            releasability="this is yet another description field",
            organisation_uuid=str(org1.uuid),
            org_id=org1.id,
            sync_user_id=0,
            active=True,
            local=True,
            created=datetime.now(),
            modified=datetime.now(),
        )

    async with AsyncExitStack() as stack:

        async def add_to_db(elem):
            return await stack.enter_async_context(DBManager(db, elem))

        ret = {}

        site_admin_user_token = encode_token(site_admin_user.id)

        role_publisher = standard_roles.publisher_role()
        role_publisher.id = None
        role_publisher = await add_to_db(role_publisher)

        role_read_only = standard_roles.read_only_role()
        role_read_only.id = None
        role_read_only = await add_to_db(role_read_only)

        role_user = standard_roles.user_role()
        role_user.id = None
        role_user = await add_to_db(role_user)

        all_roles = [role_publisher, role_read_only, role_user]

        # create orgs and users
        for i in range(1, 4):
            ret[f"org{i}"] = await add_to_db(generate_organisation(i))

            for role in all_roles:
                ret[f"user_org{i}_{role.name}"] = await add_to_db(generate_user(ret[f"org{i}"], role))
                ret[f"user_org{i}_{role.name}_clear_key"] = f"user_org{i}_{role.name}".replace("_", "").ljust(40, "0")
                ret[f"user_org{i}_{role.name}_auth_key"] = await add_to_db(
                    generate_auth_key(ret[f"user_org{i}_{role.name}_clear_key"], ret[f"user_org{i}_{role.name}"].id)
                )
                ret[f"user_org{i}_{role.name}_token"] = encode_token(ret[f"user_org{i}_{role.name}"].id)

        # create sharing groups
        # need to greate sg_org1_org2, sg_org1_org3, sg_org2_org3
        ret["sg_org1_org2"] = await add_to_db(generate_sharing_group(ret["org1"], ret["org2"]))
        await add_to_db(SharingGroupOrg(sharing_group_id=ret["sg_org1_org2"].id, org_id=ret["org1"].id))
        await add_to_db(SharingGroupOrg(sharing_group_id=ret["sg_org1_org2"].id, org_id=ret["org2"].id))
        ret["sg_org1_org3"] = await add_to_db(generate_sharing_group(ret["org1"], ret["org3"]))
        await add_to_db(SharingGroupOrg(sharing_group_id=ret["sg_org1_org3"].id, org_id=ret["org1"].id))
        await add_to_db(SharingGroupOrg(sharing_group_id=ret["sg_org1_org3"].id, org_id=ret["org3"].id))
        ret["sg_org2_org3"] = await add_to_db(generate_sharing_group(ret["org2"], ret["org3"]))
        await add_to_db(SharingGroupOrg(sharing_group_id=ret["sg_org2_org3"].id, org_id=ret["org2"].id))
        await add_to_db(SharingGroupOrg(sharing_group_id=ret["sg_org2_org3"].id, org_id=ret["org3"].id))

        # create events
        for i in range(1, 3):  # dont create events for org3
            for edl in EventDistributionLevels:
                for published in [False, True]:
                    s_published = f"{'un' if not published else ''}published"
                    if edl != EventDistributionLevels.SHARING_GROUP:
                        eventkey = f"event_org{i}_{edl}_{s_published}"
                        ret[eventkey] = await add_to_db(
                            Event(
                                org_id=ret[f"org{i}"].id,
                                orgc_id=ret[f"org{i}"].id,
                                user_id=site_admin_user.id,
                                uuid=libuuid.uuid4(),
                                sharing_group_id=0,
                                threat_level_id=1,
                                info=eventkey,
                                date=date(year=2024, month=2, day=13),
                                analysis=1,
                                distribution=edl,
                                published=published,
                            )
                        )
                        for adl in AttributeDistributionLevels:
                            if adl != AttributeDistributionLevels.SHARING_GROUP:
                                attributekey = f"attribute_org{i}_{edl}_{s_published}_{adl}"
                                ret[eventkey].attribute_count += 1
                                ret[attributekey] = await add_to_db(
                                    Attribute(
                                        value=attributekey,
                                        type="text",
                                        category=AttributeCategories.OTHER.value,
                                        event_id=ret[eventkey].id,
                                        distribution=adl,
                                        sharing_group_id=0,
                                    )
                                )
                            else:
                                for asg_key in ["sg_org1_org2", "sg_org1_org3", "sg_org2_org3"]:
                                    if f"org{i}" not in asg_key:
                                        # we skip creating events for orgs not in the sharing group
                                        continue
                                    attributekey = f"attribute_org{i}_{edl}_{s_published}_{adl}_{asg_key}"
                                    ret[eventkey].attribute_count += 1
                                    ret[attributekey] = await add_to_db(
                                        Attribute(
                                            value=attributekey,
                                            type="text",
                                            category=AttributeCategories.OTHER.value,
                                            event_id=ret[eventkey].id,
                                            distribution=adl,
                                            sharing_group_id=ret[asg_key].id,
                                        )
                                    )

                    else:
                        for sg_key in ["sg_org1_org2", "sg_org1_org3", "sg_org2_org3"]:
                            if f"org{i}" not in sg_key:
                                # we skip creating events for orgs not in the sharing group
                                continue
                            eventkey = f"event_org{i}_{edl}_{sg_key}_{s_published}"
                            ret[eventkey] = await add_to_db(
                                Event(
                                    org_id=ret[f"org{i}"].id,
                                    orgc_id=ret[f"org{i}"].id,
                                    user_id=site_admin_user.id,
                                    uuid=libuuid.uuid4(),
                                    sharing_group_id=ret[sg_key].id,
                                    threat_level_id=1,
                                    info=eventkey,
                                    date=date(year=2024, month=2, day=13),
                                    analysis=1,
                                    distribution=edl,
                                    published=published,
                                )
                            )
                            for adl in AttributeDistributionLevels:
                                if adl != AttributeDistributionLevels.SHARING_GROUP:
                                    ret[eventkey].attribute_count += 1
                                    attributekey = f"attribute_org{i}_{edl}_{sg_key}_{s_published}_{adl}"
                                    ret[attributekey] = await add_to_db(
                                        Attribute(
                                            value=attributekey,
                                            type="text",
                                            category=AttributeCategories.OTHER.value,
                                            event_id=ret[eventkey].id,
                                            distribution=adl,
                                            sharing_group_id=0,
                                        )
                                    )
                                else:
                                    for asg_key in ["sg_org1_org2", "sg_org1_org3", "sg_org2_org3"]:
                                        if f"org{i}" not in asg_key:
                                            # we skip creating events for orgs not in the sharing group
                                            continue
                                        attributekey = f"attribute_org{i}_{edl}_{sg_key}_{s_published}_{adl}_{asg_key}"
                                        ret[eventkey].attribute_count += 1
                                        ret[attributekey] = await add_to_db(
                                            Attribute(
                                                value=attributekey,
                                                type="text",
                                                category=AttributeCategories.OTHER.value,
                                                event_id=ret[eventkey].id,
                                                distribution=adl,
                                                sharing_group_id=ret[asg_key].id,
                                            )
                                        )

        default_tag = generate_tag()
        default_tag.user_id = site_admin_user.id
        default_tag.org_id = ret["org1"].id
        default_tag.is_galaxy = False
        default_tag.exportable = True

        default_tag = await add_to_db(default_tag)

        default_tag_2 = generate_tag()
        default_tag_2.user_id = site_admin_user.id
        default_tag_2.org_id = ret["org1"].id
        default_tag_2.is_galaxy = False
        default_tag_2.exportable = True

        default_tag_2 = await add_to_db(default_tag_2)

        tag_no_access = generate_tag()
        tag_no_access.user_id = site_admin_user.id
        tag_no_access.org_id = ret["org1"].id
        tag_no_access.is_galaxy = False
        tag_no_access.exportable = True

        tag_no_access = await add_to_db(tag_no_access)

        await db.commit()

        yield {
            "site_admin_user": site_admin_user,
            "site_admin_user_token": site_admin_user_token,
            "site_admin_user_clear_key": site_admin_user_clear_key,
            "site_admin_user_auth_key": site_admin_user_auth_key,
            "default_tag": default_tag,
            "default_tag_2": default_tag_2,
            "tag_no_access": tag_no_access,
            **ret,
        }
    await db.commit()


def cache_report():
    print("Hash Secret Cache", mmisp.util.crypto.hash_secret.cache_info())
    print("Verify Secret Cache", mmisp.util.crypto.verify_secret.cache_info())


atexit.register(cache_report)
