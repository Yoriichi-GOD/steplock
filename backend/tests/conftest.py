from steplock.config import ROOT

# Pytest creates the final --basetemp directory, but not missing parent folders.
(ROOT/"runtime").mkdir(exist_ok=True)
