import environ


def read_env():
    env = environ.Env(
        DEBUG=(bool, False),
        LOG_DB_SQL=(bool, False),
        SECRET_KEY=(str, 'secret'),
        DATABASE_URL=(str, ''),
        ADMIN_URL_SUFFIX=(str, 'unsafe'),
    )

    env.read_env()

    return env
