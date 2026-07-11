# glide_sms/pkg_resources.py
# Shim to make pkg_resources available even if setuptools isn't fully loaded

import sys
import importlib

# Force setuptools to load pkg_resources
try:
    import setuptools
    import pkg_resources
except ImportError:
    # If setuptools is missing, create a minimal stub
    class DistributionNotFound(Exception):
        pass

    def get_distribution(name):
        return None

    class pkg_resources:
        DistributionNotFound = DistributionNotFound
        get_distribution = staticmethod(get_distribution)

# Make pkg_resources available in sys.modules
sys.modules['pkg_resources'] = pkg_resources
