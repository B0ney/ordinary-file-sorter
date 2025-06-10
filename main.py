#! /usr/bin/python

''' Main program'''
import re
import os.path
import shutil
import json
import sys
from typing import Iterable, List, Optional, Tuple
from enum import Enum

class Action(Enum):
    DELETE = "DELETE"
    MOVE = "MOVE"
    COPY = "COPY"
    SHRED = "SHRED"

    @staticmethod
    def move(src: str, dest: str):
        try:
            shutil.move(src, dest)
            print(f"Moved: {dest} <-- {src}")

        except Exception as error:
            print(f"Move failed: {error}")

    @staticmethod
    def copy(src: str, dest: str):
        try:
            shutil.copy(src, dest)
            print(f"Copied: {dest} <-- {src}")

        except Exception as error:
            print(f"Copy failed: {error}")

class FileKind(Enum):
    ANY = "ANY"
    BINARY = "BINARY"
    PLAINTEXT = "PlAINTEXT"


# def check_kind(path: str) -> Optional[FileKind]:
#     try:
#         with open(path, "rb") as file:
#             file.re
#             pass

#     except:
#         return None

class Folder():
    ''' Stores the folder name and its full path'''
    def __init__(self, name: str, path: str):
        self.name   = name
        self.path   = path

class File():
    ''' Stores the file name, file extension and its full path.\n
        "name" is purely the file name.\n
        "extensions" can include a delimiter "." but is discouraged\n
        "path" defines the full path of a file.
    '''
    def __init__(self, name: str, extension: str, path: str):
        self.name       = name
        self.extension  = extension
        self.path       = path

class FileRule():
    ''' Used as a filter for files with the following properties:\n
        * key words -> E.g. "screenshot" or "wallpaper".\n
        * extensions -> E.g. "zip", "7z" or "".\n
        * whitelist -> (OPTIONAL) Ignore filenames if it matches an exact word from a whitelist. E.g. "icon".\n
        * action -> COPY, MOVE, DELETE
        * destination -> Where files should be moved if it satisfies the criteria above.
    '''
    def __init__(
        self,
        keywords:       List[str],
        extensions:     List[str],
        action:         str,
        destination:    str,
        whitelist:      List[str] = None,
        kind:           FileKind = FileKind.ANY,
    ):
        assert not (extensions is None and keywords is None)
        
        self.keywords       = keywords
        self.extensions     = extensions
        self.whitelist      = whitelist
        self.action         = action
        self.destination    = destination
        self.kind           = kind

def create_file_rule(
    destination:    str,
    extensions:     List[str]   = None,
    keywords:       List[str]   = None,
    whitelist:      List[str]   = None,
    action:         str         = Action.MOVE,
    kind:           FileKind    = FileKind.ANY,
) -> FileRule:
    ''' Creates a FileRule object given these parameters'''
    return FileRule(
        keywords    = keywords,
        extensions  = extensions,
        destination = destination,
        whitelist   = whitelist,
        action      = action,
        kind        = kind,
    )

class FolderTemplate():
    ''' Given a root folder and a list of folder names,
        we can generate folders with this template.
    '''
    def __init__(self,
        root_folder:        str,
        folders:            List[str],
        place_for_unwanted: Optional[str] = None
    ):
        self.root_folder          = root_folder
        self.folders              = folders
        self.place_for_unwanted   = place_for_unwanted

    @property
    def as_iter(self) -> Iterable[str]: # too much rust influence
        '''Produces a list of folders with their raw path'''
        return map(lambda folder: os.path.join(self.root_folder, folder), self.folders)

class Operation():
    ''' Stores a list of sources and a list of rules'''
    def __init__(self, scan_sources: List[str], rules: List[FileRule]):
        self.scan_sources   = scan_sources
        self.rules          = rules

class  Token():
    ''' Stores the Source of a file/folder and the destination'''
    def __init__(self, source: str, destination: str, action: str):
        self.source         = source
        self.destination    = destination
        self.action         = action

    def __repr__(self) -> str:
        '''Debugging purposes'''
        return f"Token {{is valid: '{self.is_valid()}' }}  {{ action: '{self.action}' }}  {{ dest: '{self.destination}' }}  {{ source: '{self.source}' }}"

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, source_path: str):
        self.__source = os.path.normpath(os.path.expanduser(source_path))

    @property
    def destination(self):
        return self.__destination

    @destination.setter
    def destination(self, dest_path: str):
        if dest_path is not None:
            self.__destination   = os.path.normpath(os.path.expanduser(dest_path))
        else: self.__destination = None

    def is_valid(self) -> bool:
        ''' A move token is valid if:\n
            * The source exists.
            * The source and destination parent folders are NOT equal.\n
                e.g "~/Downloads/cheese.txt" -> "~/Downloads/" is not valid.\n
            * The source folder is NOT the folder that contains this program.\n
            * The source is not this program.
        '''
        if not os.path.exists(self.source):
            return False

        if os.path.isdir(self.source):
            source_folder   = self.source
            program_path    = os.path.dirname(os.path.realpath(__file__))

        else: # Strip the filename to unveil the source folder
            source_folder   = os.path.dirname(self.source)
            program_path    = os.path.realpath(__file__)

        check_1: bool = source_folder   != self.destination
        check_2: bool = self.source     != program_path

        return check_1 and check_2

class Config():
    ''' The configuration for our file sorting.
        Stores a list of FolderTemplates and a list of FileOperations
    '''
    def __init__(
        self,
        folder_templates:   List[FolderTemplate],
        operations:         List[Operation]
    ):
        self.folder_templates   = folder_templates
        self.operations         = operations

    def export(self, file_path: str):
        '''Serialize Config class to JSON'''
        with open(file_path, "w", encoding="UTF-8") as out_file:
            json.dump(self, out_file, indent = 2, default=lambda o: o.__dict__)

        print(f"Successfully exported to {file_path}")

class Enforcer():
    '''Responsible for enforcing rules and configurations set up by the Config class.'''
    def __init__(self, config: Config):
        self.config:            Config          = config
        self.tokens:            List[Token]     = []
        self.files:             List[File]      = []
        self.folders:           List[Folder]    = []
        self.scanned_sources:   List[File]      = []

    def generate_folders(self):
        '''Generates folders when provided a list of folder templates.'''
        for folder_template in self.config.folder_templates:
            for folder in folder_template.as_iter:
                folder = os.path.expanduser(folder)

                if os.path.exists(folder):
                    print(f"INFO: Ignored folder (Already exists): '{folder}'.")
                    continue

                try:
                    os.makedirs(folder)
                    print(f"INFO: Created folder: '{folder}'")

                except Exception as err:
                    print(f"WARN: Could not create folder: '{folder}', {err}")

    def sort_folders(self):
        ''' Move folders not specified by the folder template to a specified folder.\n
            Folder templates that do not have a dedicated place for these folders are ignored. 
        '''
        move_tokens: List[Token] = []

        for template in self.config.folder_templates:

            if template.place_for_unwanted is None:
                continue

            (_, scanned_folders) = scan_dir(template.root_folder)

            for folder in scanned_folders:
                if folder.name not in template.folders:
                    move_tokens.append(Token(
                        folder.path, template.place_for_unwanted, Action.MOVE))

        self.tokens += move_tokens

    def sort_files(self):
        ''' Move files based on their extensions, keywords and whitelist status to a specified location.
        '''
        for operation in self.config.operations:
            for source in operation.scan_sources:
                self.scan_files(source)

            for rule in operation.rules:
                filtered_files = self.filter_files(rule)
                self.tokens += self.generate_file_move_tokens(rule, filtered_files)

            self.files.clear()
            self.folders.clear()
            self.scanned_sources.clear()

    def scan_files(self, path: str):
        '''A user can choose to scan multiple folders before enforcing a rule(s)'''
        if path in self.scanned_sources:
            print(f"WARN: Scanning operation ignored: Source '{path}' already scanned")

        else:
            (scanned_files, _) = scan_dir(path)
            self.files += scanned_files
            self.scanned_sources.append(path)

            print(f"INFO: Scanned {path}. {len(scanned_files)} files scanned")

    def filter_files(self, rule: FileRule) -> List[File]:
        ''' Filtering order: whitelist -> file extension -> key words '''
        filtered_files: List[File] = self.files

        if rule.whitelist is not None:
            filtered_files = Filter.by_whitelist(filtered_files, rule.whitelist)

        if rule.extensions is not None:
            filtered_files = Filter.by_extension(filtered_files, rule.extensions)

        if rule.keywords is not None:
            filtered_files = Filter.by_key_word(filtered_files, rule.keywords)

        return filtered_files

    def generate_file_move_tokens(self, rule: FileRule, filtered_files: List[File]) -> List[Token]:
        ''' Generates a list of MoveTokens given a file rule and a list of File objects'''

        return [Token(file.path, rule.destination, rule.action) for file in filtered_files]

    def enforce(self):
        '''After we generate some tokens, we use them to sort files!'''
        if self.tokens == []:
            print("\nThere's nothing to do!")
            return

        for token in self.tokens:
            if not token.is_valid():
                # print("Skipped invalid token...")
                continue

            if token.action == Action.DELETE:
                # TODO: move to recycle bin
                print("Deleting file not implemented...")
                continue

            if not os.path.exists(token.destination):
                os.makedirs(token.destination)

            src = check_and_rename_dupes(token.source, token.destination)

            if token.action == Action.MOVE:
                Action.move(src, token.destination)

            elif token.action == Action.COPY:
                Action.copy(src, token.destination)

            else:
                print(f"Action:'{token.action}' not implemented.")

        print("\nDone!")

def scan_dir(folder: str) -> Tuple[List[File], List[Folder]]:
    '''Scan a directory, return a tuple of scanned files and folders'''
    folder = os.path.expanduser(folder)

    if not os.path.exists(folder):
        raise Exception(f"Path '{folder}' does not exist!")

    files = os.scandir(folder)

    scanned_files   = []
    scanned_folders = []

    for file in files:
        (name, extension) = os.path.splitext(os.path.basename(file))
        path = os.path.abspath(file)

        if file.is_file():
            scanned_files.append(File(name, extension.strip("."), path))

        if file.is_dir():
            scanned_folders.append(Folder(name, path))

    return (scanned_files, scanned_folders)


class Filter:
    @staticmethod
    def by_whitelist(files: List[File], whitelist: List[str]) -> List[File]:
        ''' Return a list of Files that is not whitelisted '''

        return [file for file in files if file.name not in whitelist]


    @staticmethod
    def by_extension(files: List[File], extensions: List[str]) -> List[File]:
        ''' Return a list Files with extensions that were specified '''

        extensions = [ext.strip(".") for ext in extensions]
        return [file for file in files if file.extension.lower() in extensions]


    @staticmethod
    def by_key_word(list_of_files: List[File], words: List[str]) -> List[File]:
        ''' Return a list of Files if their filenames contain a particular word'''

        # TODO sanitise words in list to get rid of special characters
        regex = f"{'|'.join(words)}"

        matches = lambda string: re.search(regex, string)
        return [file for file in list_of_files if matches(file.name.lower())]

# -------------------------!! Sloppy stuff, but works !!--------------------------

def check_and_rename_dupes(source: str, destination: str) -> str:
    ''' Renames a duplicate file/folder.
        Needs refactoring
    '''
    old_file = source
    (path, file_name) = os.path.split(source)
    potential_destination = os.path.join(destination, file_name)
    path_exists = os.path.exists(potential_destination)

    if not path_exists:
        return source

    generation = 1
    (file_name, extension) = os.path.splitext(os.path.basename(file_name))

    while path_exists:
        new_file_name = f"{file_name} ({generation}){extension}"
        potential_destination = os.path.join(destination, new_file_name)
        path_exists = os.path.exists(potential_destination)
        generation += 1

    new_source_path_name = os.path.join(path,new_file_name)
    os.rename(old_file, new_source_path_name)
    print(f"Renamed duplicate file: {source} -> {new_source_path_name}")
    return new_source_path_name

def load_config(config_path: str) -> Config:
    '''A rough implementation, creates a config class from a .json'''
    with open(config_path, "r", encoding="UTF-8") as file:
        a = json.load(file)

    templates: List[FolderTemplate] = []
    operations: List[Operation]     = []

    for b in a["folder_templates"]:
        templates.append(
            FolderTemplate(
                root_folder         = b["root_folder"],
                folders             = b["folders"],
                place_for_unwanted  = b["place_for_unwanted"]
            )
        )
    for c in a["operations"]:
        file_rules: List[FileRule] = []

        for rule in c["rules"]:
            file_rules.append(
                FileRule(
                    extensions  = rule["extensions"],
                    keywords    = rule["keywords"],
                    whitelist   = rule["whitelist"],
                    destination = rule["destination"],
                    action      = rule["action"]
                )
            )

        operations.append(
            Operation(
                scan_sources    = c["scan_sources"],
                rules           = file_rules
            )
        )

    return Config(templates, operations)

# -------------------------!! sloppy stuff ends here  !!--------------------------

def main(argv):
    '''_'''
    print("Epic File Sorter by B0ney\n")
    exit_prompt = True    

    try:
        config_path = argv[0]
        new_config: Config = load_config(config_path)

    except FileNotFoundError:
        print(f"ERROR: Invalid path {config_path}")
        return
    except IndexError:
        print("ERROR: \n    You need to provide a config file! E.g. \"./configs/default.json\"")
        return

    try:
        param = argv[1]
        if param == "-Q": # quiet mode, disables exit prompt
            exit_prompt = False
    except: ## bad practice
        pass         

    test_conf = Enforcer(new_config)
    test_conf.generate_folders()
    test_conf.sort_folders()
    test_conf.sort_files()
    test_conf.enforce()

    if exit_prompt:
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main(sys.argv[1:])

    
