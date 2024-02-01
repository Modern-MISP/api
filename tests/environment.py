from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mmisp.api.auth import encode_token
from mmisp.api.main import app
from mmisp.db.database import get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.server import Server
from mmisp.db.models.user import User

from .generators.organisation_generator import generate_organisation
from .generators.role_generator import generate_site_admin_role
from .generators.user_generator import generate_user

db: Session = get_db()

instance_owner_org = generate_organisation()

db.add(instance_owner_org)

db.flush()

instance_server = Server(name="instance server", org_id=instance_owner_org.id)
site_admin_role = generate_site_admin_role()

db.add_all([instance_server, site_admin_role])

db.flush()

site_admin_user = generate_user()
site_admin_user.org_id = instance_owner_org.id
site_admin_user.server_id = instance_server.id
site_admin_user.role_id = site_admin_role.id

db.add(site_admin_user)
db.commit()


class EnvironmentType:
    def __init__(
        self: "EnvironmentType",
        instance_owner_org: Organisation,
        instance_server: Server,
        site_admin_role: Role,
        site_admin_user: User,
        site_admin_user_token: str,
    ) -> None:
        self.instance_owner_org = instance_owner_org
        self.instance_server = instance_server
        self.site_admin_role = site_admin_role
        self.site_admin_user = site_admin_user
        self.site_admin_user_token = site_admin_user_token


environment: EnvironmentType = EnvironmentType(
    instance_owner_org=instance_owner_org,
    instance_server=instance_server,
    site_admin_role=site_admin_role,
    site_admin_user=site_admin_user,
    site_admin_user_token=encode_token(site_admin_user.id),
)

client = TestClient(app)
