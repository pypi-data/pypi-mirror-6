default: buildout test

buildout: bin/buildout buildout-cache/downloads
	bin/buildout -c buildout.cfg -N -t 3

test:
	bin/test
	bin/flake8 plonesocial

bin/buildout: bin/python
	bin/easy_install zc.buildout==1.7.1
	bin/easy_install distribute==0.6.28

bin/python:
	virtualenv --clear --no-site-packages --distribute .

buildout-cache/downloads:
	[ -d buildout-cache ] || mkdir -p buildout-cache/downloads

clean:
	rm -rf bin/* .installed.cfg parts/download

