PACKAGE = local/package.sh

.PHONY:	clean dist

clean:
	$(PACKAGE) clean || true

dist:
	$(PACKAGE) dist
