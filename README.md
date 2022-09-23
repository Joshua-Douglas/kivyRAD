# Kivy Designer
A development tool for rapid cross platform application development using Python.

# Developer Setup
This project uses `pipenv` for dependency management.
```
# Install with development dependencies (e.g. pytest, etc.)
$ pipenv install --dev

# Install without development dependencies
$ pipenv install
```

If for any reason you encounter installation issue, you should be able to utilize the pipfile.lock for a safe, deterministic build. 

Please submit an issue if this approach is needed:
```
$ pipenv install --ignore-pipfile
```