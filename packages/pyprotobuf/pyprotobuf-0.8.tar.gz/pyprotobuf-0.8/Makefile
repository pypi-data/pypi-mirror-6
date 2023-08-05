NAME=protopy
TESTS=${NAME}.tests
NOSEFLAGS=--cover-html --cover-erase --cover-inclusive ${NAME} --cover-branches
NOSEFLAGS+=--cover-package=${NAME}
NOSEFLAGS+=-v -d

all: pylint test

testdata:
	mkdir -p testdata
	
.PHONY pylint: testdata/pylint.out testdata/pylint.html

testdata/pylint.out: testdata
	pylint --rcfile=.pylintrc --output-format=parseable newsengine | tee $@ > /dev/null

testdata/pylint.html: testdata
	pylint --rcfile=pylintrc --output-format=html --rcfile=.pylintrc ${NAME} | tee $@ > /dev/null
	
PYTHON_REQ=requirements.txt

testenvprep: ${PYTHON_REQ}
	# run this before running tests
	pip install -r ${PYTHON_REQ}
	
testenvprep_local: ${PYTHON_REQ}
	# unpack requirements provided on a local url
	pip install -v 	--find-links=file://$(shell pwd)/external --no-index --index-url=file:///dev/null -r ${PYTHON_REQ}
	
test:
	env nosetests ${NOSEFLAGS} ${TESTS} 

clean:
	rm dist -rf
	rm build -rf

