PACKAGE:=
VERSION:=$(shell git describe --dirty)
all:
	@echo no default rule

lint:
	echo nothing to lint

clean:
	rm -f dummy-binary

install:
	echo nothing to lint

BUILD_DEP:= \
	build-essential \

.PHONY: build-dep
build-dep:
	sudo apt install $(BUILD_DEP)

.PHONY: dpkg
dpkg:
	rm -f debian/changelog
	dch --create --empty --package $(PACKAGE) -v ${VERSION}-0 --no-auto-nmu local package Auto Build
	dpkg-buildpackage -rfakeroot -us -uc
	mv ../*.deb ./

.PHONY: deploy
deploy:
	echo nothing to deploy
