def test_hello_world():
    # Simple smoke test to verify pytest discovers unit tests
    greeting = "Hola mundo"
    assert greeting.startswith("Hola")


def test_math_basic():
    # Basic arithmetic check
    assert 2 + 2 == 4
