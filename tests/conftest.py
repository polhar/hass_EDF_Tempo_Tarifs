"""Fixtures for tests."""
import pytest
import threading

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in tests."""
    yield


@pytest.fixture(autouse=True)
def expected_lingering_tasks():
    """Allow lingering tasks for all tests."""
    return True


@pytest.fixture(autouse=True)
def expected_lingering_timers():
    """Allow lingering timers for all tests."""
    return True
    
@pytest.fixture(autouse=True)
def patch_thread_check(monkeypatch):
    """Patch thread verification to allow Home Assistant shutdown threads."""
    # Patch la vérification des threads pour accepter les threads de shutdown HA
    original_enumerate = threading.enumerate
    
    def patched_enumerate():
        """Filter out Home Assistant shutdown threads."""
        threads = original_enumerate()
        return [
            t for t in threads 
            if not (hasattr(t, 'name') and '_run_safe_shutdown_loop' in t.name)
        ]
    
    monkeypatch.setattr(threading, 'enumerate', patched_enumerate)
    yield
