def test_environment_ready():
    import fastapi
    import langgraph
    import playwright
    import pydantic
    import sqlglot

    assert pydantic.__version__.startswith("2.")
    assert all([fastapi, langgraph, playwright, sqlglot])
