# Changelog

All notable changes to ArchiPy are documented in this changelog, organized by version.


## [0.13.2] - 2025-04-10

### Documentation

- Enhanced Redis adapter documentation with comprehensive docstrings
- Added MinIO adapter to API reference documentation

### Code Quality

- Improved code quality with linter fixes across Redis adapter and ORM components
- Fixed file utilities test suite
- Cleaned up redundant changelog files

## [0.13.1] - 2025-04-08

### Security

- Enhanced cryptographic security by replacing `random` with `secrets` module
- Strengthened TOTP implementation with improved security practices
- Upgraded password utilities with robust validation and generation

### Code Quality

- Improved type safety with explicit typing and modern type hints
- Enhanced error handling with domain-specific exception types
- Standardized parameter naming and module consistency

### Documentation

- Added comprehensive docstrings to configuration classes
- Expanded utility function documentation
- Improved error handling documentation

## [0.13.0] - 2025-04-08

### Features

- **MinIO Integration**: Full S3-compatible object storage adapter with:
  - Comprehensive S3 operation support (12 standardized methods)
  - Built-in TTL caching for performance optimization
  - Flexible configuration with endpoint and credential management
  - Clear cache management through `clear_all_caches`

### Testing

- Added complete BDD test suite for MinIO adapter:
  - Bucket and object operation validation
  - Presigned URL generation testing
  - Bucket policy management verification

### Documentation

- Added extensive MinIO adapter examples and usage guides
- Improved error handling documentation
- Updated configuration documentation with new MinIO settings

### Usage Example

```python
# Initialize the MinIO adapter
from archipy.adapters.minio.adapters import MinioAdapter
minio = MinioAdapter()

# Create a bucket and upload a file
minio.make_bucket("my-bucket")
minio.put_object("my-bucket", "document.pdf", "/path/to/document.pdf")

# Generate a presigned URL for temporary access
download_url = minio.presigned_get_object("my-bucket", "document.pdf", expires=3600)
```

## [0.12.0] - 2025-03-29

### Features

- **Keycloak Integration**: Comprehensive authentication and authorization for FastAPI:
  - Role-based access control with customizable requirements
  - Resource-based authorization for fine-grained access control
  - Both synchronous and asynchronous authentication flows
  - Token validation and introspection
  - User info extraction capabilities

### Code Quality

- Improved error handling clarity by renaming `ExceptionMessageType` to `ErrorMessageType`
- Enhanced error documentation with detailed descriptions
- Updated error handling implementation with new message types

### Usage Example

```python
from fastapi import FastAPI, Depends
from archipy.helpers.utils.keycloak_utils import KeycloakUtils

app = FastAPI()

@app.get("/api/profile")
def get_profile(user: dict = Depends(KeycloakUtils.fastapi_auth(
    required_roles={"user"},
    admin_roles={"admin"}
))):
    return {
        "user_id": user.get("sub"),
        "username": user.get("preferred_username")
    }
```

## [0.11.2] - 2025-03-21

### Error Handling

- Enhanced exception management with improved error reporting
- Streamlined error messaging for better debugging
- Fixed various error handling edge cases

## [0.11.1] - 2025-03-15

### Performance

- Optimized resource usage across core components
- Enhanced caching mechanisms for improved performance
- Improved memory utilization in key operations

## [0.11.0] - 2025-03-10

### Features

- **Keycloak Adapter**: New authentication and authorization system:
  - Asynchronous operations support
  - Token management and validation
  - User information retrieval
  - Comprehensive security features

### Performance

- Added TTL cache decorator for optimized performance
- Improved Keycloak adapter efficiency

### Documentation

- Added detailed Keycloak integration guides
- Included comprehensive usage examples

### Usage Example

```python
from archipy.adapters.keycloak.adapters import KeycloakAdapter

# Initialize adapter with configuration from global config
keycloak = KeycloakAdapter()

# Authenticate and get access token
token = keycloak.get_token("username", "password")

# Get user information
user_info = keycloak.get_userinfo(token)

# Verify token validity
is_valid = keycloak.validate_token(token)
```

## [0.10.2] - 2025-03-05

### Stability

- Improved Redis connection pool stability and management
- Enhanced error recovery mechanisms
- Fixed various edge cases in Redis operations

## [0.10.1] - 2025-03-01

### Documentation

- Enhanced Redis and email adapter documentation
- Added comprehensive API reference
- Improved usage examples for common operations

## [0.10.0] - 2025-02-25

### Features

- **Redis Integration**: New caching and key-value storage system:
  - Flexible key-value operations
  - Built-in TTL support
  - Connection pooling
  - Comprehensive error handling

- **Email Service**: New email integration system:
  - Multiple email provider support
  - Template-based email sending
  - Attachment handling
  - Async operation support

### Configuration

- Enhanced configuration management system
- Added support for Redis and email settings
- Improved environment variable handling

### Usage Example

```python
# Initialize the Redis adapter
from archipy.adapters.redis.adapters import RedisAdapter
redis = RedisAdapter()

# Basic operations
redis.set("user:1:name", "John Doe")
name = redis.get("user:1:name")

# Using with TTL
redis.set("session:token", "abc123", ttl=3600)  # Expires in 1 hour
```

## [0.9.0] - 2025-02-20

### Security

- **TOTP System**: Comprehensive Time-based One-Time Password implementation:
  - Secure token generation and validation
  - Configurable time windows
  - Built-in expiration handling
  - RFC compliance

- **Multi-Factor Authentication**: Enhanced security framework:
  - Multiple authentication factor support
  - Flexible factor configuration
  - Integration with existing auth systems

### Usage Example

```python
from archipy.helpers.utils.totp_utils import TOTPUtils
from uuid import uuid4

# Generate a TOTP code
user_id = uuid4()
totp_code, expires_at = TOTPUtils.generate_totp(user_id)

# Verify a TOTP code
is_valid = TOTPUtils.verify_totp(user_id, totp_code)

# Generate a secure key for TOTP initialization
secret_key = TOTPUtils.generate_secret_key_for_totp()
```

## [0.8.0] - 2025-02-15

### Features

- **Redis Integration**: Comprehensive key-value store and caching system:
  - Full Redis API implementation
  - Built-in caching functionality
  - Performance-optimized operations
  - Connection pooling support

### Testing

- **Mock Redis Implementation**:
  - Complete test coverage for Redis operations
  - Simulated Redis environment for testing
  - Configurable mock behaviors

### Documentation

- Added Redis integration guides
- Included mock testing examples
- Updated configuration documentation

## [0.7.2] - 2025-02-10

### Database

- Enhanced connection pool stability and management
- Improved transaction isolation and handling
- Optimized error reporting for database operations
- Added connection lifecycle management

## [0.7.1] - 2025-02-05

### Performance

- Optimized query execution and planning
- Reduced memory footprint for ORM operations
- Enhanced connection pool efficiency
- Improved cache utilization

## [0.7.0] - 2025-02-01

### Features

- **SQLAlchemy Integration**: Complete ORM implementation:
  - Robust entity model system
  - Transaction management with ACID compliance
  - Connection pooling with configurable settings
  - Comprehensive database operations support

### Usage Example

```python
from archipy.adapters.orm.sqlalchemy.adapters import SQLAlchemyAdapter
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity
from sqlalchemy import Column, String

# Define a model
class User(BaseEntity):
    __tablename__ = "users"
    name = Column(String(100))
    email = Column(String(100), unique=True)

# Use the ORM
orm = SQLAlchemyAdapter()
with orm.session() as session:
    # Create and read operations
    new_user = User(name="John Doe", email="john@example.com")
    session.add(new_user)
    session.commit()

    user = session.query(User).filter_by(email="john@example.com").first()
```

## [0.6.1] - 2025-01-25

### Stability

- Fixed memory leaks in gRPC interceptors
- Improved interceptor performance and efficiency
- Enhanced request/response handling reliability
- Optimized resource cleanup

## [0.6.0] - 2025-01-20

### Features

- **gRPC Integration**: Comprehensive interceptor system:
  - Client and server-side interceptors
  - Request/response monitoring
  - Performance tracing capabilities
  - Enhanced error management

### Documentation

- Added gRPC integration guides
- Included interceptor configuration examples
- Updated troubleshooting documentation

## [0.5.1] - 2025-01-15

### Stability

- Enhanced FastAPI middleware reliability
- Improved response processing efficiency
- Optimized request handling performance
- Fixed edge cases in error management

## [0.5.0] - 2025-01-10

### Features

- **FastAPI Integration**: Complete web framework support:
  - Custom middleware components
  - Request/response processors
  - Standardized error handling
  - Response formatting utilities

### Documentation

- Added FastAPI integration guides
- Included middleware configuration examples
- Updated API documentation

## [0.4.0] - 2025-01-05

### Features

- **Configuration System**: Flexible environment management:
  - Environment variable support
  - Type-safe configuration validation
  - Default value management
  - Override capabilities

### Documentation

- Added configuration system guides
- Included environment setup examples
- Updated validation documentation

## [0.3.0] - 2024-12-25

### Features

- **Core Utilities**: Comprehensive helper functions:
  - Date/time manipulation with timezone support
  - String processing and formatting
  - Common development utilities
  - Type conversion helpers

### Documentation

- Added utility function reference
- Included usage examples
- Updated API documentation

## [0.2.0] - 2024-12-20

### Architecture

- **Hexagonal Architecture**: Core implementation:
  - Ports and adapters pattern
  - Clean architecture principles
  - Domain-driven design
  - Base entity models

### Documentation

- Added architecture overview
- Included design pattern guides
- Updated component documentation

## [0.1.0] - 2025-02-21

### Features

- **Initial Release**: Project foundation:
  - Core project structure
  - Basic framework components
  - Configuration system
  - CI/CD pipeline with GitHub Actions

### Documentation

- Added initial documentation
- Included getting started guide
- Created contribution guidelines
