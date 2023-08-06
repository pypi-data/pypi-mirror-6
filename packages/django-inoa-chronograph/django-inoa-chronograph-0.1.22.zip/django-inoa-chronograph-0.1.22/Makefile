rpm: clean
	mkdir dist
ifneq "$(BUILD_NUMBER)" ""
	python setup.py bdist_rpm --release=$(BUILD_NUMBER)
else
	python setup.py bdist_rpm --release=0.`date +'%s'`.test
endif

upload: clean
	mkdir dist
	python setup.py sdist bdist upload -r tim

clean:
	python setup.py clean
	rm -rf build
	rm -rf dist
	rm -rf MANIFEST