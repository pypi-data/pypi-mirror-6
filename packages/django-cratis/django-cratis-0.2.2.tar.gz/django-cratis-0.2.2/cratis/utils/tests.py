from contextlib import contextmanager
import inject

@contextmanager
def inject_services(configurator):
    inject.clear_and_configure(configurator)
    yield
    inject.clear()
