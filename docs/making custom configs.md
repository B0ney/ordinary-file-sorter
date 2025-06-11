# Custom Configs
It is recommended that paths in your user profile are prefixed with "**~**".

E.g.  "/home/B0ney/Downloads" -> "**~**/Downloads"

The configuration has two main parts:
* **folder_templates**
* **operations**

### Folder Templates
A **Template** has the following properties:
* **root_folder**: Where should we place our generated folders?
* **folders**:  A list of folders to generate.
* **place_for_unwanted**: Scanned folders that are **not** in **folders** are treated as "**unwanted**". 
 If the user wishes to move these "**unwanted**" folders somewhere, the destination folder goes here. Otherwise it should be **None**.

### Operations
An **Operation** has the following properties:

* **scan_sources**: A list of folders to scan.
* **rules**: A list of rules. Filter files based on the properties defined by a rule.

A **Rule** has the following properties:
* **extensions**: A list of extensions to sort files with. **E.g [ "exe" ,  "msi" ]**
* **key_words**: A list of words to sort files with. **E.g [ "wallpaper" ,  "screenshot" ]** (not case sensitive).
* **whitelist**: If you have a specific file you **don't** want to be sorted, put the them here. (TODO: do you provide a full path or just the file+extension?) 
* **destination**: If a file matches the properties above, we must provide a folder to move them to.

You **must** have at least either **extensions** or **key_words** defined. i.e  **extensions** and **key_words** cannot be both **None**

#### Quirks
To sort files that **do not have** an extension, the **extensions** field must be: **[ "" ]**.

If you want to move every file regardless, the **key_words** field must be **[""]**.

**NOTE**: Every rule is enforced **serially**, that means the order at which you add these rules matter!

#### Warnings
In an **Operation**, It is possible to create an unwanted cycle. This can occur if a folder in **scan_sources** also exists in a **Rule's** destination.

Here's an example of an **Operation** with a cycle: 

```json
...

{
  "scan_sources": [
		"~/Downloads",
		"~/Pictures",
		"~/Downloads/Unsorted"
	],
	"rules": [
		{
			"key_words": null,
			"extensions": [
				"jpg"
			],
			"destination": "~/Pictures/",
			"whitelist": null
		},
		{
			"key_words": "",
			"extensions": null,
			"destination": "~/Downloads/Unsorted/",
			"whitelist": null
		}
	]
},
...

```

This may not seem obvious, but let's break it down:

We will be scanning folders: "**~/Downloads**", "**~/Pictures/**" and "**~/Downloads/Unsorted**".

The rules will be enforced in order.

The **first rule** means that if we find a ".jpg" file in those **three** folders, we move it to "**~/Pictures**".

The **second rule** means that we move every file we find in those **three** folders, regardless of name or extension to **~/Downloads/Unsorted**.

**What happens**:

|Runs| ~/Downloads | ~/Pictures | ~/Downloads/Unsorted|
|---|---|---|---|
|0 (initial)| cat.jpg | | |
|1| ---> | cat.jpg| |
|2|  | ---> | cat.jpg|
|3|  | cat.jpg| <---|
|4|  |---> | cat.jpg|

Before we enforce any rules, the program will keep a "record" of all the files scanned, this will be handy later.

0) We have downloaded a nice photo **cat.jpg**.
1) When the operation is enforced, the first rule has an affect: **cat.jpg** is moved to **~/Pictures**. The second rule doesn't do anything because the file no longer exists according to the "record".
2) When we run the second time, the first rule doesn't do anything because **cat.jpg** is already at its destination. The second rule does, so **cat.jpg** is moved to **~/Downloads/Unsorted**.
3) Basically a repeat  of 1)

**The Solution**

The last rule is the cause of this cycle. Create a new separate operation: 
```json
...
{
	"scan_sources": [
		"~/Downloads",
		"~/Pictures",
		"~/Downloads/Unsorted"
	],
	"rules": [
		{
			"key_words": null,
			"extensions": [
				"jpg"
			],
			"destination": "~/Pictures/",
			"whitelist": null
		},
	]
},
{
	"scan_sources": [
		"~/Downloads",
	],
	"rules": [
		{
			"key_words": "",
			"extensions": null,
			"destination": "~/Downloads/Unsorted/",
			"whitelist": null
		}
	]
},
...

```