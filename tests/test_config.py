from os import environ

import pytest

from tiebreakserver.core.config import get_settings


@pytest.mark.config
class TestConfig:
    @pytest.mark.select
    @pytest.mark.config
    def test_get_settings(self):
        settings = get_settings()
        assert settings.INSTALLER_USERID == environ.get("INSTALLER_USERID")
        assert settings.INSTALLER_PWD == environ.get("INSTALLER_PWD")
        assert settings.MYSQL_HOST == environ.get("MYSQL_HOST")
        assert settings.MYSQL_TCP_PORT == int(environ.get("MYSQL_TCP_PORT"))
        assert settings.MYSQL_DATABASE == environ.get("MYSQL_DATABASE")
        assert settings.MYSQL_PWD == environ.get("MYSQL_PWD")
        assert settings.MYSQL_ROOT_PASSWORD == environ.get("MYSQL_ROOT_PASSWORD")
        assert settings.VENV_ENVIRONMENT == environ.get("VENV_ENVIRONMENT")

        print(f"""\nINSTALLER_USERID:\t\t{settings.INSTALLER_USERID}\t{environ.get("INSTALLER_USERID")}""")
        print(f"""INSTALLER_PWD:\t\t\t{settings.INSTALLER_PWD}\t{environ.get("INSTALLER_PWD")}""")
        print(f"""MYSQL_HOST:\t\t\t\t{settings.MYSQL_HOST}\t{environ.get("MYSQL_HOST")}""")
        print(f"""MYSQL_TCP_PORT:\t\t\t{settings.MYSQL_TCP_PORT}\t\t{int(environ.get("MYSQL_TCP_PORT"))}""")
        print(f"""MYSQL_DATABASE:\t\t\t{settings.MYSQL_DATABASE}\t{environ.get("MYSQL_DATABASE")}""")
        print(f"""MYSQL_PWD:\t\t\t\t{settings.MYSQL_PWD}\t{environ.get("MYSQL_PWD")}""")
        print(f"""MYSQL_ROOT_PASSWORD:\t{settings.MYSQL_ROOT_PASSWORD}\t{environ.get("MYSQL_ROOT_PASSWORD")}""")
        print(f"""VENV_ENVIRONMENT:\t\t{settings.VENV_ENVIRONMENT}\t\t{environ.get("VENV_ENVIRONMENT")}""")
        pass
