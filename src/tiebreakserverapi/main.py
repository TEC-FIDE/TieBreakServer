from fastapi import FastAPI
from reahl.webdeclarative.webdeclarative import UserSession
from rtedb.tables import accounting
from rtedb.tables import address
from rtedb.tables import chess_titles
from rtedb.tables import country
from rtedb.tables import emailaddr
from rtedb.tables import identification
from rtedb.tables import organization
from rtedb.tables import person
from rtedb.tables import phone

from rteapi.routers.address import router as rtr_address
from rteapi.routers.address_organization_org_type import router as rtr_address_organization_org_type
from rteapi.routers.address_person import router as rtr_address_person
from rteapi.routers.address_type import router as rtr_address_type
from rteapi.routers.auth import router as rtr_auth
from rteapi.routers.bank_acc_detail import router as rtr_bank_acc_detail
from rteapi.routers.citizenship import router as rtr_citizenship
from rteapi.routers.country import router as rtr_country
from rteapi.routers.email_and_password_system_account import router as rtr_email_and_password_system_account
from rteapi.routers.emailaddr import router as rtr_emailaddr
from rteapi.routers.emailaddr_org import router as rtr_emailaddr_org
from rteapi.routers.emailaddr_person import router as rtr_emailaddr_person
from rteapi.routers.emailaddr_type import router as rtr_emailaddr_type
from rteapi.routers.identification import router as rtr_identification
from rteapi.routers.identification_type import router as rtr_identification_type
from rteapi.routers.member_type import router as rtr_member_type
from rteapi.routers.occupation_type import router as rtr_occupation_type
from rteapi.routers.org_type import router as rtr_org_type
from rteapi.routers.organization import router as rtr_organization
from rteapi.routers.organization_org_type import router as rtr_organization_org_type
from rteapi.routers.person import router as rtr_person
from rteapi.routers.person_org_portfolio import router as rtr_person_org_portfolio
from rteapi.routers.person_organization_org_type import router as rtr_person_organization_org_type
from rteapi.routers.phone import router as rtr_phone
from rteapi.routers.phone_org import router as rtr_phone_org
from rteapi.routers.phone_person import router as rtr_phone_person
from rteapi.routers.phone_type import router as rtr_phone_type
from rteapi.routers.portfolio import router as rtr_portfolio
from rteapi.routers.portfolio_status import router as rtr_portfolio_status
from rteapi.routers.race import router as rtr_race
from rteapi.routers.race_surname import router as rtr_race_surname
from rteapi.routers.registration_type import router as rtr_registration_type
from rteapi.routers.verify import router as rtr_verify


# These assignments are used to trick the linters.  The imports above must be
# there for SqlAlchemy to access the definitions
dummy_accounting = accounting
dummy_address = address
dummy_chess_titles = chess_titles
dummy_country = country
dummy_emailaddr = emailaddr
dummy_identification = identification
dummy_organization = organization
dummy_person = person
dummy_phone = phone
dummy_user_session = UserSession


app = FastAPI()
app.include_router(rtr_address)
app.include_router(rtr_address_organization_org_type)
app.include_router(rtr_address_person)
app.include_router(rtr_address_type)
app.include_router(rtr_auth)
app.include_router(rtr_bank_acc_detail)
app.include_router(rtr_citizenship)
app.include_router(rtr_country)
app.include_router(rtr_email_and_password_system_account)
app.include_router(rtr_emailaddr)
app.include_router(rtr_emailaddr_org)
app.include_router(rtr_emailaddr_person)
app.include_router(rtr_emailaddr_type)
app.include_router(rtr_identification)
app.include_router(rtr_identification_type)
app.include_router(rtr_member_type)
app.include_router(rtr_occupation_type)
app.include_router(rtr_org_type)
app.include_router(rtr_organization)
app.include_router(rtr_organization_org_type)
app.include_router(rtr_person)
app.include_router(rtr_person_org_portfolio)
app.include_router(rtr_person_organization_org_type)
app.include_router(rtr_phone)
app.include_router(rtr_phone_org)
app.include_router(rtr_phone_person)
app.include_router(rtr_phone_type)
app.include_router(rtr_portfolio)
app.include_router(rtr_portfolio_status)
app.include_router(rtr_race)
app.include_router(rtr_race_surname)
app.include_router(rtr_registration_type)
app.include_router(rtr_verify)


@app.get('/ping')
async def ping():
    return {'msg': 'pong'}
