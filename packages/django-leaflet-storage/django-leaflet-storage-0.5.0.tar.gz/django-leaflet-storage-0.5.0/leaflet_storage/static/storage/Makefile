.PHONY: test
test:
	firefox test/index.html
i18n:
	node reqs/i18n/bin/i18n.js --dir_path=src/js/ --locale_dir_path=src/locale/ --locale_codes=en --mode=json --clean
tx_push:
	tx push -s
tx_pull:
	tx pull