# Program architechture

There's a lot of code, so how does it all work?

The program first scans a directory.
All files and folders are added to a list respectively.

When we're sorting files, we check if a file satisfies a criteria. If a file matches a criteria, a token is generated.

A token stores a path to a file/folder, its destination and an action ("MOVE", "COPY", "DELETE")

This token is then used to sort files.

A token has built-in protective measures to minimise error. 

