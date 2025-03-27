# features/keycloak_auth.feature
Feature: Keycloak Authentication Testing
  As a developer
  I want to test Keycloak authentication operations
  So that I can ensure secure authentication without a real Keycloak server

  Background:
    Given a Keycloak realm "test-realm" exists
    And a client "service" exists
    And the "VERIFY_PROFILE" required action is disabled in realm "test-realm"
    And client "test-client" has client authentication enabled
    And client "test-client" has service accounts roles enabled
    And client "test-client" has "manage-users" and "manage-realm" service account role access

  Scenario: Obtain token with valid credentials using sync adapter
    Given a configured sync Keycloak adapter
    And a user exists with username "testuser" and password "pass123"
    When I request a token with username "testuser" and password "pass123" using sync adapter
    Then the sync token request should succeed
    And the sync token response should contain "access_token" and "refresh_token"

  Scenario: Refresh token using sync adapter
    Given a configured sync Keycloak adapter
    And a user exists with username "testuser" and password "pass123"
    And I have a valid token for "testuser" with password "pass123" using sync adapter
    When I refresh the token using sync adapter
    Then the sync token refresh should succeed
    And the sync token response should contain "access_token" and "refresh_token"

  Scenario: Get user info with sync adapter
    Given a configured sync Keycloak adapter
    And a user exists with username "testuser" and password "pass123"
    And I have a valid token for "testuser" with password "pass123" using sync adapter
    When I request user info with the token using sync adapter
    Then the sync user info request should succeed
    And the sync user info should contain "sub" and "preferred_username"

  Scenario: Logout user with sync adapter
    Given a configured sync Keycloak adapter
    And a user exists with username "testuser" and password "pass123"
    And I have a valid token for "testuser" with password "pass123" using sync adapter
    When I logout the user using sync adapter
    Then the sync logout operation should succeed

  Scenario: Validate token with sync adapter
    Given a configured sync Keycloak adapter
    And a user exists with username "testuser" and password "pass123"
    And I have a valid token for "testuser" with password "pass123" using sync adapter
    When I validate the token using sync adapter
    Then the sync token validation should succeed

  @async
  Scenario: Obtain token asynchronously with valid credentials
    Given a configured async Keycloak adapter
    And a user exists with username "asyncuser" and password "async123"
    When I request a token with username "asyncuser" and password "async123" using async adapter
    Then the async token request should succeed
    And the async token response should contain "access_token" and "refresh_token"

  @async
  Scenario: Refresh token asynchronously
    Given a configured async Keycloak adapter
    And a user exists with username "asyncuser" and password "async123"
    And I have a valid token for "asyncuser" with password "async123" using async adapter
    When I refresh the token using async adapter
    Then the async token refresh should succeed
    And the async token response should contain "access_token" and "refresh_token"

  @async
  Scenario: Get user info asynchronously
    Given a configured async Keycloak adapter
    And a user exists with username "asyncuser" and password "async123"
    And I have a valid token for "asyncuser" with password "async123" using async adapter
    When I request user info with the token using async adapter
    Then the async user info request should succeed
    And the async user info should contain "sub" and "preferred_username"

  @async
  Scenario: Logout user asynchronously
    Given a configured async Keycloak adapter
    And a user exists with username "asyncuser" and password "async123"
    And I have a valid token for "asyncuser" with password "async123" using async adapter
    When I logout the user using async adapter
    Then the async logout operation should succeed

  @async
  Scenario: Validate token asynchronously
    Given a configured async Keycloak adapter
    And a user exists with username "asyncuser" and password "async123"
    And I have a valid token for "asyncuser" with password "async123" using async adapter
    When I validate the token using async adapter
    Then the async token validation should succeed
