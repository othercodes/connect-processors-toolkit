import uuid

from connect.processors_toolkit.helpers import validator


def test_validator_should_validate_values():
    def validate_name(name: str) -> None:
        if len(name) < 3:
            raise ValueError(f'Invalid name <{name}>.')

    errors, valid = validator(
        [uuid.UUID, validate_name],
        ['5338d5e4-6f3e-45fe-8af5-e2d96213b3f0', 'Po'],
    )

    assert len(errors) == 1
    assert str(errors[0]) == 'Invalid name <Po>.'

    assert len(valid) == 1
    assert isinstance(valid[0], uuid.UUID)
