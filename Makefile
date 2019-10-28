build:
	docker build -t docs-or-not .

filter:
	docker run -v ${src}:/src-dir -v ${dest}:/dest-dir docs-or-not filter /src-dir /dest-dir

filter_inplace:
	docker run -v ${src}:/src-dir -v ${dest}:/dest-dir docs-or-not filter_inplace /src-dir /dest-dir