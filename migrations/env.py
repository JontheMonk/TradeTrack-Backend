from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context

from core.settings import settings
from data.models import Base

# ---------------------------------------------------------
# Alembic Config + Logging
# ---------------------------------------------------------
config = context.config
fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


# ---------------------------------------------------------
# OFFLINE MODE
# ---------------------------------------------------------
def run_migrations_offline():
    """Run migrations without a live DB connection."""
    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# ONLINE MODE
# ---------------------------------------------------------
def run_migrations_online():
    """Run migrations with an active DB engine."""
    connectable = create_engine(settings.database_url, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
