from mmisp.db.models.galaxy import Galaxy


def generate_galaxy() -> Galaxy:
    return Galaxy(
        name="test galaxy",
        type="test type",
        description="test",
        version="version",
        kill_chain_order="test kill_chain_order",
    )
