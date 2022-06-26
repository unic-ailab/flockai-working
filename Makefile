all: clean package install

package:
	python3 setup.py sdist bdist_wheel

install:
	python3 -m pip install --no-cache-dir --upgrade --target=$(PYTHONPATH) dist/flockai*.whl

requirements:
	python3 -m pip install --user -r requirements.txt

clean:
	sudo -S rm -r dist/* build/*

