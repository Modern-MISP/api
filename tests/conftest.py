from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self, Tuple

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

import mmisp.lib.standard_roles as standard_roles
from mmisp.api.auth import encode_token
from mmisp.api.main import init_app
from mmisp.db.models.admin_setting import AdminSetting
from mmisp.db.models.event import EventTag
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.db.models.role import Role
from mmisp.db.models.sharing_group import SharingGroupOrg, SharingGroupServer
from mmisp.db.models.user import User
from mmisp.db.models.workflow import Workflow
from mmisp.tests.fixtures import *  # noqa
from mmisp.tests.generators.model_generators.attribute_generator import generate_attribute
from mmisp.tests.generators.model_generators.event_generator import generate_event
from mmisp.tests.generators.model_generators.tag_generator import generate_tag
from mmisp.tests.generators.model_generators.user_generator import generate_user
from mmisp.tests.generators.model_generators.user_setting_generator import generate_user_name
from mmisp.tests.generators.model_generators.organisation_generator import generate_organisation
from mmisp.tests.generators.model_generators.sharing_group_generator import generate_sharing_group
from mmisp.tests.generators.model_generators.role_generator import generate_read_only_role
from mmisp.lib.distribution import EventDistributionLevels, AttributeDistributionLevels
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


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app()


@pytest_asyncio.fixture
async def sharing_group_org(db, sharing_group, instance_owner_org):
    sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=instance_owner_org.id)
    db.add(sharing_group_org)
    await db.commit()
    yield sharing_group_org
    await db.delete(sharing_group_org)
    await db.commit()


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
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = site_admin_user.id

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def event4(db, organisation, site_admin_user):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = site_admin_user.id

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def event5(db, organisation, site_admin_user):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = site_admin_user.id

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
        collection_uuid="uuid",
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
async def role_read_modify_only(db):
    role = Role(
        id=43,
        name="test_read_modify_only",
        perm_add=False,
        perm_modify=True,
        perm_modify_org=True,
        perm_publish=True,
        perm_delegate=False,
        perm_sync=False,
        perm_admin=False,
        perm_audit=False,
        perm_auth=True,
        perm_site_admin=False,
        perm_regexp_access=False,
        perm_tagger=True,
        perm_template=False,
        perm_sharing_group=False,
        perm_tag_editor=True,
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
async def access_test_user(db, instance_owner_org):
    user = User(
        password="very_safe_passwort",
        org_id=instance_owner_org.id,
        role_id=43,
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


@pytest.fixture
def access_test_user_token(access_test_user):
    return encode_token(access_test_user.id)


@pytest_asyncio.fixture
async def event_read_only_1(db, organisation, access_test_user):
    org_id = access_test_user.org_id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = access_test_user.id
    event.published = False
    event.distribution = 0

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def event_read_only_2(db, organisation, access_test_user):
    org_id = organisation.id
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = access_test_user.id
    event.published = False
    event.distribution = 0

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def event_test_wrong_org(db, site_admin_user):
    org_id = 9999
    event = generate_event()
    event.org_id = org_id
    event.orgc_id = org_id
    event.user_id = site_admin_user.id
    event.published = False
    event.distribution = 0

    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def attribute_read_only_1(db, event_read_only_1):
    event_id = event_read_only_1.id
    attribute = generate_attribute(event_id)
    attribute.distribution = 0
    event_read_only_1.attribute_count += 1

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(attribute)
    event_read_only_1.attribute_count -= 1
    await db.commit()


@pytest_asyncio.fixture
async def attribute_read_only_2(db, event_test_wrong_org):
    event_id = event_test_wrong_org.id
    attribute = generate_attribute(event_id)
    attribute.distribution = 0
    event_test_wrong_org.attribute_count += 1

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(attribute)
    event_test_wrong_org.attribute_count -= 1
    await db.commit()


@pytest_asyncio.fixture
async def tag_read_only_1(db, access_test_user):
    tag = generate_tag()
    tag.user_id = access_test_user.id
    tag.org_id = access_test_user.org_id

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture
async def eventtag_read_only_1(db, event, tag):
    eventtag = EventTag(event_id=event.id, tag_id=tag.id, local=False)

    db.add(eventtag)
    await db.commit()
    await db.refresh(eventtag)

    yield eventtag

    await db.delete(eventtag)
    await db.commit()


@pytest_asyncio.fixture
async def access_test_objects(db, site_admin_user):
    default_org = generate_organisation()
    db.add(default_org)
    await db.commit()
    await db.refresh(default_org)
    default_org_id = default_org.id

    org_no_users = generate_organisation()
    db.add(org_no_users)
    await db.commit()
    await db.refresh(org_no_users)

    default_sharing_group_org = generate_organisation()
    db.add(default_sharing_group_org)
    await db.commit()
    await db.refresh(default_sharing_group_org)
    sharing_group_org_id = default_sharing_group_org.id

    default_sharing_group = generate_sharing_group()
    default_sharing_group.organisation_uuid = default_sharing_group_org.uuid
    default_sharing_group.org_id = sharing_group_org_id
    db.add(default_sharing_group)
    await db.commit()
    await db.refresh(default_sharing_group)

    default_role_modify = Role(
        id=44,
        name="test_read_modify_only",
        perm_add=False,
        perm_modify=True,
        perm_modify_org=True,
        perm_publish=True,
        perm_delegate=False,
        perm_sync=False,
        perm_admin=False,
        perm_audit=False,
        perm_auth=True,
        perm_site_admin=False,
        perm_regexp_access=False,
        perm_tagger=True,
        perm_template=False,
        perm_sharing_group=False,
        perm_tag_editor=True,
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

    db.add(default_role_modify)
    await db.commit()
    await db.refresh(default_role_modify)
    """
    default_role_read_only = Role(
        id=45,
        name="default_role_read_only",
        perm_add=False,
        perm_modify=False,
        perm_modify_org=False,
        perm_publish=False,
        perm_delegate=False,
        perm_sync=False,
        perm_admin=False,
        perm_audit=False,
        perm_auth=True,
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

    db.add(default_role_read_only)
    await db.commit()
    await db.refresh(default_role_read_only)
    """

    default_user = User(
        password="very_safe_passwort",
        org_id=default_org_id,
        role_id=default_role_modify.id,
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
    db.add(default_user)
    await db.commit()
    await db.refresh(default_user)
    default_user_id = default_user.id
    """
    default_read_only_user = User(
        password="very_safe_passwort",
        org_id=default_org_id,
        role_id=default_role_read_only.id,
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
    db.add(default_read_only_user)
    await db.commit()
    await db.refresh(default_read_only_user)
    """
    default_event = generate_event()
    default_event.org_id = default_org_id
    default_event.orgc_id = default_org_id
    default_event.user_id = default_user_id
    default_event.published = False
    default_event.distribution = EventDistributionLevels.OWN_ORGANIZATION

    db.add(default_event)
    await db.commit()
    await db.refresh(default_event)
    default_event_id = default_event.id

    event_no_access = generate_event()
    event_no_access.org_id = org_no_users.id
    event_no_access.orgc_id = org_no_users.id
    event_no_access.user_id = site_admin_user.id
    event_no_access.published = False
    event_no_access.distribution = EventDistributionLevels.OWN_ORGANIZATION

    db.add(event_no_access)
    await db.commit()
    await db.refresh(event_no_access)
    event_no_access_id = event_no_access.id

    event_dist_sg = generate_event()
    event_dist_sg.org_id = default_org_id
    event_dist_sg.orgc_id = default_org_id
    event_dist_sg.user_id = site_admin_user.id
    event_dist_sg.published = True
    event_dist_sg.distribution = EventDistributionLevels.SHARING_GROUP
    event_dist_sg.sharing_group_id = default_sharing_group.id

    db.add(event_dist_sg)
    await db.commit()
    await db.refresh(event_dist_sg)

    default_attribute = generate_attribute(default_event_id)
    default_attribute.distribution = 0
    default_event.attribute_count += 1

    db.add(default_attribute)
    await db.commit()
    await db.refresh(default_attribute)

    attribute_no_access = generate_attribute(event_no_access_id)
    attribute_no_access.distribution = 0
    event_no_access.attribute_count += 1

    db.add(attribute_no_access)
    await db.commit()
    await db.refresh(attribute_no_access)

    default_tag = generate_tag()
    default_tag.user_id = default_user_id
    default_tag.org_id = default_org_id

    db.add(default_tag)
    await db.commit()
    await db.refresh(default_tag)

    tag_no_access = generate_tag()
    tag_no_access.user_id = site_admin_user.id
    tag_no_access.org_id = org_no_users.id

    db.add(tag_no_access)
    await db.commit()
    await db.refresh(tag_no_access)

    dict == {
        "site_admin_user": site_admin_user,
        "site_admin_user_token": encode_token(site_admin_user.id),
        "default_org": default_org,
        "org_no_users": org_no_users,
        "default_sharing_group_org": default_sharing_group_org,
        "default_sharing_group": default_sharing_group,
        "default_role_modify": default_role_modify,
        #"default_role_read_only": default_role_read_only,
        "default_user": default_user,
        #"default_read_only_user": default_read_only_user,
        "default_user_token": encode_token(default_user.id),
        #"default_read_only_user_token": encode_token(default_read_only_user.id),
        "default_event": default_event,
        "event_no_access": event_no_access,
        "event_dist_sg": event_dist_sg,
        "default_attribute": default_attribute,
        "attribute_no_access": attribute_no_access,
        "default_tag": default_tag,
        "tag_no_access": tag_no_access,
    }

    yield dict

    await db.delete(tag_no_access)
    await db.delete(default_tag)
    await db.delete(attribute_no_access)
    event_no_access.attribute_count -= 1
    await db.delete(default_attribute)
    default_event.attribute_count -= 1
    await db.delete(event_dist_sg)
    await db.delete(event_no_access)
    await db.delete(default_event)
    #await db.delete(default_read_only_user)
    await db.delete(default_user)
    #await db.delete(default_role_read_only)
    await db.delete(default_role_modify)
    await db.delete(default_sharing_group_org)
    await db.delete(org_no_users)
    await db.delete(default_org)

    await db.commit()
