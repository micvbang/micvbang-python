rm -r build/ dist/ micvbang.egg-info/
python3 setup.py sdist bdist_wheel
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
rm -r build/ dist/ micvbang.egg-info/
