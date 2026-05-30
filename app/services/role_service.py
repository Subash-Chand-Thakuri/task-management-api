from app.models.role import Role
from app.models.role import RoleNameEnum

def get_role_by_name(name: RoleNameEnum) -> Role:
    return Role(id=1, name=name)