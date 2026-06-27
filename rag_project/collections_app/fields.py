from django.db import models
from snowflake import SnowflakeGenerator

# Machine ID 1 — change this per server instance in multi-server deployments
_generator = SnowflakeGenerator(1)


def generate_snowflake_id():
    return next(_generator)


class SnowflakeIDField(models.BigIntegerField):
    """
    A BigIntegerField that auto-generates a Snowflake ID as the default.
    We use BigIntegerField because Snowflake IDs are 64-bit integers —
    Django's default AutoField is only 32-bit and would overflow.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', generate_snowflake_id)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('unique', True)
        super().__init__(*args, **kwargs)
