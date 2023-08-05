polaris.js: \
	app.js \
	utils.js \
	controllers/* \
	directives/* \
	services/*

polaris.js:
	@rm -f $@
	cat $(filter %.js,$^) > $@

clean:
	rm -f polaris*.js
