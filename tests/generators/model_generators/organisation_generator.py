from mmisp.db.models.organisation import Organisation


def generate_organisation() -> Organisation:
    return Organisation(
        name="ORGNAME",
        description="auto-generated org",
        type="another free text description",
        nationality="earthian",
        sector="software",
        created_by=0,
        contacts="Test Org\r\nBuilding 42\r\nAdenauerring 7\r\n76131 Karlsruhe\r\nGermany",
        local=True,
        restricted_to_domain="",  # TODO seems like there is a stringified json array saved in text, not sure
        landingpage="",
    )
