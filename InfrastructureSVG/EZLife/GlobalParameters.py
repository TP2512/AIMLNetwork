from dataclasses import dataclass, field

from InfrastructureSVG.Jira_Infrastructure.FieldsConstructor.FieldsConstructor import get_full_field_list
from InfrastructureSVG.EZLife.ReadByType import ReadFromUser


@dataclass
# class GlobalParameters:
class EZLifeGlobalParameters:
    user_jira_credentials: str = 'TestspanAuto'
    ezlife_ip_address: str = '192.168.126.181'  # Production
    # ezlife_ip_address: str = '192.168.126.189'  # Aviz Dev
    ezlife_port: str = '8000'
    base_url: str = f'http://{ezlife_ip_address}:{ezlife_port}'
    api_token = "Token e0be8ef44386d94471d1d0cd3ca95db95853eef3"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': api_token}

    field_list: list = field(default_factory=lambda: get_full_field_list())


@dataclass
class GlobalClassAndFunctions:
    read_from_user_fn: ReadFromUser = ReadFromUser()
