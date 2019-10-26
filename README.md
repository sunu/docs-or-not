# DOC-OR-NOT

Detects if a picture is a picture of a document or not. Filters out pictures of documents from a folder of pictures.

## How to run

- Run `make build` to build the docker image
- Run `make filter src="/path/to/source" dest="/path/to/destination"` to copy pictures of documents from the source
folder to the destination folder. The folder structure is retained while copying.
