Lockable-dev


#Building and pushing changes
```
#Build
python setup.py sdist bdist_wheel

#Upload latest version to TestPyPi
python -m twine upload — repository testpypi dist/*
```
