from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mmisp.api.auth import encode_token
from mmisp.api.main import app
from mmisp.db.database import get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.server import Server
from mmisp.db.models.user import User

from .generators.model_generators.organisation_generator import generate_organisation
from .generators.model_generators.role_generator import generate_org_admin_role, generate_site_admin_role
from .generators.model_generators.user_generator import generate_user

db: Session = get_db()

instance_owner_org = generate_organisation()
instance_org_two = generate_organisation()
instance_two_owner_org = generate_organisation()
instance_two_owner_org.local = False

db.add_all([instance_owner_org, instance_org_two, instance_two_owner_org])
db.flush()

instance_two_server = Server(name="Instance Two Server", org_id=instance_two_owner_org.id)

site_admin_role = generate_site_admin_role()
org_admin_role = generate_org_admin_role()

db.add_all([instance_two_server, site_admin_role, org_admin_role])
db.flush()

site_admin_user = generate_user()
site_admin_user.org_id = instance_owner_org.id
site_admin_user.server_id = 0
site_admin_user.role_id = site_admin_role.id

instance_owner_org_admin_user = generate_user()
instance_owner_org_admin_user.org_id = instance_owner_org.id
instance_owner_org_admin_user.server_id = 0
instance_owner_org_admin_user.role_id = org_admin_role.id

instance_org_two_admin_user = generate_user()
instance_org_two_admin_user.org_id = instance_org_two.id
instance_org_two_admin_user.server_id = 0
instance_org_two_admin_user.role_id = org_admin_role.id

instance_two_owner_org_admin_user = generate_user()
instance_two_owner_org_admin_user.org_id = instance_two_owner_org.id
instance_two_owner_org_admin_user.server_id = instance_two_server.id
instance_two_owner_org_admin_user.role_id = org_admin_role.id

db.add_all(
    [site_admin_user, instance_owner_org_admin_user, instance_org_two_admin_user, instance_two_owner_org_admin_user]
)
db.commit()


class EnvironmentType:
    def __init__(
        self: "EnvironmentType",
        instance_owner_org: Organisation,
        instance_org_two: Organisation,
        instance_two_owner_org: Organisation,
        instance_two_server: Server,
        site_admin_role: Role,
        org_admin_role: Role,
        site_admin_user: User,
        instance_owner_org_admin_user: User,
        instance_org_two_admin_user: User,
        instance_two_owner_org_admin_user: User,
        site_admin_user_token: str,
        instance_owner_org_admin_user_token: str,
        instance_two_owner_org_admin_user_token: str,
        instance_org_two_admin_user_token: str,
    ) -> None:
        self.instance_owner_org = instance_owner_org
        self.instance_org_two = instance_org_two
        self.instance_two_owner_org = instance_two_owner_org

        self.instance_two_server = instance_two_server

        self.site_admin_role = site_admin_role
        self.org_admin_role = org_admin_role

        self.site_admin_user = site_admin_user
        self.instance_owner_org_admin_user = instance_owner_org_admin_user
        self.instance_org_two_admin_user = instance_org_two_admin_user
        self.instance_two_owner_org_admin_user = instance_two_owner_org_admin_user

        self.site_admin_user_token = site_admin_user_token
        self.instance_owner_org_admin_user_token = instance_owner_org_admin_user_token
        self.instance_two_owner_org_admin_user_token = instance_two_owner_org_admin_user_token
        self.instance_org_two_admin_user_token = instance_org_two_admin_user_token


environment: EnvironmentType = EnvironmentType(
    instance_owner_org=instance_owner_org,
    instance_org_two=instance_org_two,
    instance_two_owner_org=instance_two_owner_org,
    instance_two_server=instance_two_server,
    site_admin_role=site_admin_role,
    org_admin_role=org_admin_role,
    site_admin_user=site_admin_user,
    instance_owner_org_admin_user=instance_owner_org_admin_user,
    instance_org_two_admin_user=instance_org_two_admin_user,
    instance_two_owner_org_admin_user=instance_two_owner_org_admin_user,
    site_admin_user_token=encode_token(site_admin_user.id),
    instance_owner_org_admin_user_token=encode_token(instance_owner_org_admin_user.id),
    instance_two_owner_org_admin_user_token=encode_token(instance_two_owner_org_admin_user.id),
    instance_org_two_admin_user_token=encode_token(instance_org_two_admin_user.id),
)

client = TestClient(app)


def auth_header(token: str) -> dict:
    return {"authorization": f"Bearer {token}"}
