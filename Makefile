
package:
	python3 setup.py sdist bdist_wheel

config:
	cat .pypirc > ~/.pypirc
	sudo -S chmod 600 ~/.pypirc

upload:
	python3 -m twine upload dist/*

install:
	python3 -m pip install --upgrade --target=$(PYTHONPATH) flockai

requirements:
	python3 -m pip install --user -r requirements.txt

clean:
	sudo -S rm -r dist/*
