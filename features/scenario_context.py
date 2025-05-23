import asyncio
import os


class ScenarioContext:
    """A storage class for scenario-specific objects.

    This class provides a way to store objects that are specific to a scenario,
    preventing cross-contamination between scenarios when using a shared context.
    """

    def __init__(self, scenario_id):
        """Initialize with a unique scenario ID."""
        self.scenario_id = scenario_id
        self.storage = {}
        self.db_file = None
        self.adapter = None
        self.async_adapter = None
        self.entities = {}
        self.entity_ids = {}

    def store(self, key, value):
        """Store an object with the given key."""
        self.storage[key] = value

    def get(self, key, default=None):
        """Get an object with the given key, returning default if not found."""
        return self.storage.get(key, default)

    def cleanup(self):
        """Clean up resources associated with this scenario."""
        # Close and dispose of database connections
        if self.adapter:
            try:
                if hasattr(self.adapter, "session_manager") and hasattr(self.adapter.session_manager, "engine"):
                    # First remove any open sessions
                    self.adapter.session_manager.remove_session()
                    # Then dispose of the engine
                    self.adapter.session_manager.engine.dispose()
            except Exception as e:
                print(f"Error disposing engine: {e}")

        # Clean up async adapter
        if self.async_adapter:
            try:
                if hasattr(self.async_adapter, "session_manager") and hasattr(
                    self.async_adapter.session_manager,
                    "engine",
                ):
                    # For async, we need to get a loop and run the coroutine
                    loop = asyncio.get_event_loop()
                    if not loop.is_closed():
                        try:
                            # Run the session removal coroutine
                            loop.run_until_complete(self.async_adapter.session_manager.remove_session())

                            # Run the engine disposal coroutine
                            loop.run_until_complete(self.async_adapter.session_manager.engine.dispose())
                        except Exception as e:
                            print(f"Error in async cleanup: {e}")
                    else:
                        # If the loop is closed, create a new one temporarily
                        temp_loop = asyncio.new_event_loop()
                        try:
                            asyncio.set_event_loop(temp_loop)
                            temp_loop.run_until_complete(self.async_adapter.session_manager.remove_session())
                            temp_loop.run_until_complete(self.async_adapter.session_manager.engine.dispose())
                        finally:
                            temp_loop.close()
            except Exception as e:
                print(f"Error in async cleanup: {e}")

        # Remove database file if it exists
        if self.db_file and os.path.exists(self.db_file):
            try:
                # Make sure all connections are closed before attempting to remove
                import time

                time.sleep(0.1)  # Small delay to ensure connections are fully closed
                os.remove(self.db_file)
            except Exception as e:
                print(f"Error removing database file: {e}")
