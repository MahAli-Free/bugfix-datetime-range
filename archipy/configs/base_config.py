from typing import Generic, Self, TypeVar

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from archipy.configs.config_template import (
    AuthConfig,
    DatetimeConfig,
    ElasticSearchAPMConfig,
    ElasticSearchConfig,
    EmailConfig,
    FastAPIConfig,
    FileConfig,
    GrpcConfig,
    KafkaConfig,
    KavenegarConfig,
    KeycloakConfig,
    MinioConfig,
    PrometheusConfig,
    RedisConfig,
    SentryConfig,
    SqlAlchemyConfig,
)
from archipy.configs.environment_type import EnvironmentType

"""

Priority :
            1. pypoject.toml [tool.configs]
            2. configs.toml or other toml file init
            3. .env file
            4. os level environment variable
            5. class field value
"""
R = TypeVar("R")  # Runtime Config


class BaseConfig(BaseSettings, Generic[R]):
    """Base configuration class for ArchiPy applications.

    This class provides a comprehensive configuration system that loads settings
    from multiple sources in the following priority order:

    1. pyproject.toml [tool.configs] section
    2. configs.toml or other specified TOML files
    3. Environment variables (.env file)
    4. OS-level environment variables
    5. Default class field values

    The class implements the Singleton pattern via a global config instance that
    can be set once and accessed throughout the application.

    Attributes:
        AUTH (AuthConfig): Authentication and security settings
        DATETIME (DatetimeConfig): Date/time handling configuration
        ELASTIC (ElasticSearchConfig): Elasticsearch configuration
        EMAIL (EmailConfig): Email service configuration
        ENVIRONMENT (EnvironmentType): Application environment (dev, test, prod)
        FASTAPI (FastAPIConfig): FastAPI framework settings
        REDIS (RedisConfig): Redis cache configuration
        SQLALCHEMY (SqlAlchemyConfig): Database ORM configuration

    Examples:
        >>> from archipy.configs.base_config import BaseConfig
        >>>
        >>> class MyAppConfig(BaseConfig):
        ...     # Override defaults
        ...     APP_NAME = "My Application"
        ...     DEBUG = True
        ...
        ...     # Custom configuration
        ...     FEATURE_FLAGS = {
        ...         "new_ui": True,
        ...         "advanced_search": False
        ...     }
        >>>
        >>> # Set as global configuration
        >>> config = MyAppConfig()
        >>> BaseConfig.set_global(config)
        >>>
        >>> # Access from anywhere
        >>> from archipy.configs.base_config import BaseConfig
        >>> current_config = BaseConfig.global_config()
        >>> app_name = current_config.APP_NAME  # "My Application"
    """

    model_config = SettingsConfigDict(
        case_sensitive=True,
        pyproject_toml_depth=3,
        env_file=".env",
        pyproject_toml_table_header=("tool", "configs"),
        extra="ignore",
        env_nested_delimiter="__",
        env_ignore_empty=True,
    )

    __global_config: Self | None = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            file_secret_settings,
            PyprojectTomlConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            init_settings,
        )

    AUTH: AuthConfig = AuthConfig()
    DATETIME: DatetimeConfig = DatetimeConfig()
    ELASTIC: ElasticSearchConfig = ElasticSearchConfig()
    ELASTIC_APM: ElasticSearchAPMConfig = ElasticSearchAPMConfig()
    EMAIL: EmailConfig = EmailConfig()
    ENVIRONMENT: EnvironmentType = EnvironmentType.LOCAL
    FASTAPI: FastAPIConfig = FastAPIConfig()
    FILE: FileConfig = FileConfig()
    GRPC: GrpcConfig = GrpcConfig()
    KAFKA: KafkaConfig = KafkaConfig()
    KAVENEGAR: KavenegarConfig = KavenegarConfig()
    KEYCLOAK: KeycloakConfig = KeycloakConfig()
    MINIO: MinioConfig = MinioConfig()
    PROMETHEUS: PrometheusConfig = PrometheusConfig()
    REDIS: RedisConfig = RedisConfig()
    SENTRY: SentryConfig = SentryConfig()
    SQLALCHEMY: SqlAlchemyConfig = SqlAlchemyConfig()

    def customize(self) -> None: ...

    @classmethod
    def global_config(cls) -> R:
        """Retrieves the global configuration instance.

        Returns:
            R: The global configuration instance.

        Raises:
            AssertionError: If the global config hasn't been set with
                BaseConfig.set_global()

        Examples:
            >>> config = BaseConfig.global_config()
            >>> redis_host = config.REDIS.MASTER_HOST
        """
        if cls.__global_config is None:
            raise AssertionError("You should set global configs with  BaseConfig.set_global(MyConfig())")
        return cls.__global_config

    @classmethod
    def set_global(cls, config: R) -> None:
        """Sets the global configuration instance.

        This method should be called once during application initialization
        to set the global configuration that will be used throughout the app.

        Args:
            config (R): The configuration instance to use globally.

        Examples:
            >>> my_config = MyAppConfig(BaseConfig)
            >>> BaseConfig.set_global(my_config)
        """
        config.customize()
        cls.__global_config = config
