all: clean package install

package:
	python3 setup.py sdist bdist_wheel

install:
	python3 -m pip install --no-cache-dir --upgrade --target=$(WEBOTS_PYTHON_PATH) dist/flockai*.whl

requirements:
	python3 -m pip install --user -r requirements.txt

clean:
	rm -r dist/* build/*

