''' Main program
'''
import re
import os.path
import shutil
import json
from typing import Tuple

class Folder():
    ''' Stores the folder name and its full path'''
    def __init__(self, name: str, path: str):
        self.name           = name
        self.path           = path

class File():
    ''' Stores the file name, file extension and its full path.\n
        "name" is purely the file name.\n
        "extensions" can include a delimiter "." but is discoraged\n
        "path" defines the full path of a file.
    '''
    def __init__(self, name: str, extension: str, path: str):
        self.name           = name
        self.extension      = extension
        self.path           = path

class FileRule():
    ''' Used as a filter for files with the following properties:\n
        * key words -> E.g. "screenshot" or "wallpaper".\n
        * extensions -> E.g. "zip", "7z" or "".\n
        * whitelist -> Ignore filenames if it matches an exact word from a whitelist. E.g. "icon".\n
        * destination -> Where files should be moved if it satisfies the criteria above.
    '''
    def __init__(
        self,
        key_words:      list[str],
        extensions:     list[str],
        destination:    str,
        whitelist:      list[str] = None
    ) -> None:
        self.key_words      = key_words
        self.extensions     = extensions
        self.destination    = destination
        self.whitelist      = whitelist
        # self.action

class  MoveToken():
    ''' Stores the Source of a file/folder and the destination'''
    def __init__(
        self,
        source:         str,
        destination:    str
    ) -> None:
        self.source         = source
        self.destination    = destination

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
        self.__destination = os.path.normpath(os.path.expanduser(dest_path))

    def is_valid(self) -> bool:
        ''' A move token is valid if:\n
            * The source exists.
            * The source and destination parent folders are NOT equal.\n
                e.g "~/Downloads/cheese.txt" -> "~/Downloads/" is not valid.\n
            * The source folder is NOT the folder that contains this program.\n 
        '''
        if not os.path.exists(self.source):
            return False

        if os.path.isdir(self.source):
            source_folder = self.source
            program_path =  os.path.dirname(os.path.realpath(__file__))

        else: # Strip the filename to unveil the source folder
            source_folder = os.path.dirname(self.source)
            program_path =  os.path.realpath(__file__)

        check_1: bool = source_folder   != self.destination
        check_2: bool = self.source     != program_path

        return check_1 and check_2

class FolderTemplate():
    ''' Given a root folder and a list of folder names,
        we can generate folders with this template.
    '''
    def __init__(
        self,
        root_folder:    str,
        folders:        list[str],
        unknown_folder: str = None
    ) -> None:
        self.root_folder          = root_folder
        self.folders              = folders
        self.place_for_unwanted   = unknown_folder

    @property
    def as_iter(self) -> list[str]: # too much rust influence
        '''Produces a list of folders with their raw path'''
        return map(lambda folder: os.path.join(self.root_folder, folder), self.folders)

class Operation():
    ''' Stores a list of sources and a list of rules'''
    def __init__(
        self,
        source: list[str],
        rules:  list[FileRule]
    ) -> None:
        self.scan_sources   = source
        self.rules          = rules

class Config():
    ''' The configuration for our file sorting.
        Stores a list of FolderTemplates and a list of FileOperations
    '''
    def __init__(
        self,
        folder_templates:   list[FolderTemplate] = None,
        operations:         list[Operation] = None
        ):
        self.folder_templates   = folder_templates
        self.operations    = operations

    def export(self, file_path: str):
        '''Serializes Config to JSON'''
        # TODO: add error handling
        with open(file_path, "w") as out_file:
            json.dump(self, out_file, indent = 4, default=lambda o: o.__dict__)

    # def load(self, file_path: str):
    #     pass

class Enforcer():
    '''
    Responsible for enforcing rules and configurations set up by the Config class.
    '''
    def __init__(self, config: Config):
        self.config:            Config          = config
        self.move_tokens:       list[MoveToken] = []
        self.files:             list[File]      = []
        self.folders:           list[Folder]    = []
        self.scanned_sources:   list[File]      = []

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
        '''
        Move folders not specified by the folder template to a specified folder.\n
        Folder templates that do not have a dedicated place for these folders are ignored. 
        '''
        move_tokens: list[MoveToken] = []

        for folder_template in self.config.folder_templates:

            if folder_template.place_for_unwanted is None:
                continue

            (_, scanned_folders) = scandir(folder_template.root_folder)

            for folder in scanned_folders:
                unhandled_files_dir = folder_template.place_for_unwanted
                folder_path = folder.path

                if folder.name not in folder_template.folders:
                    move_tokens.append(MoveToken(folder_path, unhandled_files_dir))

        self.move_tokens += move_tokens

    def sort_files(self):
        ''' Move files based on their extensions,
            key words and whitelist status to a specified location.
        '''
        operations = self.config.operations

        for operation in operations:
            for source in operation.scan_sources:
                self.scan_files(source)

            for rule in operation.rules:
                filtered_files = self.filter_files(rule)
                self.move_tokens += self.generate_file_move_tokens(rule, filtered_files)

            self.files              = []
            self.folders            = []
            self.scanned_sources    = []

    def scan_files(self, path: str):
        '''A user can choose to scan multiple folders before enforcing a rule(s)'''
        if path in self.scanned_sources:
            print(f"WARN: Scanning operation ignored: Source '{path}' already scanned")

        else:
            (scanned_files, _) = scandir(path)
            self.files += scanned_files
            self.scanned_sources.append(path)

            print(f"INFO: Scanned {path}. {len(scanned_files)} files scanned")

    def filter_files(self, rule: FileRule) -> list[File]:
        ''' Filtering order: whitelist -> file extension -> key words '''
        filtered_files: list[File] = self.files

        if rule.whitelist is not None:
            filtered_files = filter_by_whitelist(filtered_files, rule.whitelist)

        if rule.extensions is not None:
            filtered_files = filter_by_extension(filtered_files, rule.extensions)

        if rule.key_words is not None:
            filtered_files = filter_by_key_word(filtered_files, rule.key_words)

        return filtered_files

    def generate_file_move_tokens(
        self,
        rule: FileRule,
        filtered_files: list[File]
        ) -> list[MoveToken]:
        ''' Generates a list of MoveTokens given a file rule and a list of File objects'''
        template_list: list[MoveToken] = []

        for file in filtered_files:
            template_list.append(MoveToken(file.path, rule.destination))

        return template_list

def scandir(folder: str) -> Tuple[list[File], list[Folder]]:
    '''Scan a directory, return a tuple of scanned files and folders'''
    folder = os.path.expanduser(folder)

    if not os.path.exists(folder):
        raise Exception(f"Path '{folder}' does not exist!")

    files = os.scandir(folder)

    scanned_files = []
    scanned_folders = []

    for file in files:
        (name, extension) = os.path.splitext(os.path.basename(file))
        path = os.path.abspath(file)

        if file.is_file():
            scanned_files.append(File(name, extension.strip("."), path))

        if file.is_dir():
            scanned_folders.append(Folder(name, path))

    return (scanned_files, scanned_folders)

def move(move_token_list: list[MoveToken]):
    ''' Move files and folders according to the list of MoveTokens.\n
        Will automatically rename duplicates.\n
        Will automatically create a folder if it doesn't exist.
    '''
    for move_token in move_token_list:
        if not move_token.is_valid():
            print("Skipping invalid token...")
            continue

        move_token.source = check_and_rename_dupes(move_token.source, move_token.destination)

        if not os.path.exists(move_token.destination):
            os.makedirs(move_token.destination)
        try:
            shutil.move(move_token.source, move_token.destination)
            print(f"moved: {move_token.destination} <-- {move_token.source}")

        except Exception as error:
            print(f"Move failed: {error}")

def filter_by_whitelist(list_of_files: list[File], whitelist: list[str]) -> list[File]:
    ''' Return an iterator of non whitelisted Files '''
    return filter(lambda file: file.name not in whitelist, list_of_files)

def filter_by_extension(list_of_files: list[File], extensions: list[str]) -> list[File]:
    ''' Return an iterator that yields File objects such that their extensions are in a list '''
    return filter(lambda file: file.extension in map(lambda ext: ext.strip("."), extensions), list_of_files)

def filter_by_key_word(list_of_files: list[File], words: list[str]) -> list[File]:
    ''' Return an iterator of Files if their filenames satisfy a particluar word'''
    return filter(lambda file: re.search(as_regex(words), file.name.lower()), list_of_files)

def as_regex(list_of_key_words: list[str]) -> str:
    # TODO sanitise words in list to get rid of special characters
    return f"{'|'.join(list_of_key_words)}"

def create_file_rule(
    destination: str,
    extensions: list[str] = None,
    key_words: list[str] = None,
    whitelist: list[str] = None
    ) -> FileRule:
    ''' Creates a FileRule object given these parameters'''
    assert not (extensions is None and key_words is None)
    # raise "You must provide at least a list of extensions or a list of key words!"

    return FileRule(
        key_words,
        extensions,
        destination,
        whitelist,
    )

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

def main():
    ''' main'''
    sources = ["~/Downloads", "~/Pictures","~/Downloads/Unsorted"]
    rules: list[FileRule] = [
        create_file_rule("~/Downloads/Compressed", extensions=["zip", "7z", "tar", "bz2", "rar","xz","gz"]),
        create_file_rule("~/Downloads/Compressed/Java", extensions=["jar"]),
        create_file_rule("~/Downloads/Programs", extensions=["exe","elf","bin","deb", "rpm","msi","appimage"]),
        create_file_rule("~/Downloads/Music", extensions=["mp3","mp2","wav","ogg","aac","flac","alac","dsd","mqa","m4a"]),
        create_file_rule("~/Downloads/Music/midi", extensions=["mid"]),
        create_file_rule("~/Pictures/wallpaper", extensions=["jpeg", "jpg", "png"], key_words=["wallpaper", "unsplash"]),
        create_file_rule("~/Pictures/", extensions=["jpg"]),
        create_file_rule("~/Pictures/Screenshot", key_words=["screenshot"]),
        create_file_rule("~/Downloads/Misc/No extensions", extensions=[""]),
        create_file_rule("~/Downloads/Video", extensions=["mp4","mkv"]),
        # # create_file_rule("~/Downloads/Compressed", extensions=["zip"]),

    ]  
    operations = Operation(
        source = sources,
        rules = rules
    )
    unsorted_stuff = Operation(
        source = ["~/Downloads"],
        rules = [create_file_rule("~/Downloads/Unsorted/", key_words="")]
    )
    folder_gen = [
        FolderTemplate(
            "~/Downloads",
            [
                "Compressed",
                "Documents",
                "Pictures",
                "Music",
                "Video",
                "Programs",
                "Unsorted",
                "Misc",
                "Misc/Unsorted",
                "Misc/No extensions",
                "Misc/Folders"
            ],
            "~/Downloads/Folders"),
    ]
    config = Config(
        folder_templates = folder_gen,
        operations = [operations, unsorted_stuff]
    )

    config.export("./epic_config.json")

    enforcer = Enforcer(config)
    # # enforcer.generate_folders()
    # enforcer.sort_folders()
    enforcer.sort_files()
    move(enforcer.move_tokens)

    # print(json.dumps([operations, operations], indent = 4, default=lambda o: o.__dict__))




if __name__ == "__main__":
    main()
