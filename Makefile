build:
	docker build -t docs-or-not .

filter:
	docker run -v ${src}:/src-dir -v ${dest}:/dest-dir docs-or-not /src-dir /dest-dir