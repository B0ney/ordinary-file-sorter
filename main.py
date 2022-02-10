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
    ''' Stores the file name, file extension and its full path.'''
    def __init__(self, name: str, extension: str, path: str):
        self.name           = name
        self.extension      = extension
        self.path           = path

class FileRule():
    ''' Used as a filter for files with the following properties:\n
        * key words -> E.g. "screenshot" or "wallpaper".\n
        * extensions -> E.g. "zip", "7z" or "".\n
        * whitelist -> Filenames that exactly match words in a whitelist will be ignored. E.g. "".\n
        * destination -> Where files should be moved to if satisfies criteria above.
    '''
    def __init__(
        self,
        key_words: list[str],
        extensions: list[str],
        destination: str,
        whitelist: list[str] = None
        ):
        self.key_words      = key_words
        self.extensions     = extensions
        self.destination    = destination
        self.whitelist      = whitelist

class  MoveToken():
    ''' Stores the Source of a file/folder and the destination'''
    def __init__(self, source: str, destination: str):
        self.source         = source
        self.destination    = destination

class FolderTemplate():
    ''' Given a root folder and a list of folder names,
        we can generate folders with this template
    '''
    def __init__(
        self,
        root_folder: str,
        folders: list[str],
        unknown_folder: str = None
        ):
        self.root_folder          = root_folder
        self.folders              = folders
        self.place_for_unwanted   = unknown_folder
    
    @property
    def as_iter(self) -> list[str]: # too much rust influence
        '''Produces a list of folders with their raw path'''
        return map(lambda folder: os.path.join(self.root_folder, folder), self.folders)

class FileOperations():
    ''' With this we can scan a list of directories '''
    def __init__(self, source: list[str], rules: list[FileRule]):
        self.sources  = source
        self.rules    = rules

class Config():
    ''' The configuration for our file sorting.
        Stores a list of FolderTemplates and a list of FileOperations
    '''
    def __init__(
        self,
        folder_templates: list[FolderTemplate] = None,
        file_operations: list[FileOperations] = None
        ):
        self.folder_templates   = folder_templates
        self.file_operations    = file_operations

    def export(self, file_path: str):
        '''Serializes Config to JSON'''
        # TODO: add error handling
        out_file = open(file_path, "w")
        json.dump(self, out_file, indent = 4, default=lambda o: o.__dict__)
        out_file.close()

    def load(self, file_path: str):
        pass

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
        '''
        Generates folders when provided a list of folder templates. 
        '''
        # Perfect, no need to refactor
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
        template_with_fallback = filter_if_has_fallback(self.config.folder_templates)
        move_tokens: list[MoveToken] = []

        for folder_template in template_with_fallback:
            (_, scanned_folders) = scandir(folder_template.root_folder)

            for folder in scanned_folders:
                unhandled_files_dir = os.path.expanduser(folder_template.place_for_unwanted)
                folder_path = os.path.expanduser(folder.path)

                if folder.name not in folder_template.folders and folder_path != unhandled_files_dir:
                    move_tokens.append(MoveToken(folder_path, unhandled_files_dir))

        self.move_tokens += move_tokens

    def sort_files(self):
        '''
        Move files based on their extensions, key words and whitelist status
        to a specified location.
        '''
        operations = self.config.file_operations

        for operation in operations:
            for source in operation.sources:
                self.scan_files(source)

            for rule in operation.rules:
                filtered_files = self.filter_files(rule)
                self.move_tokens += self.generate_file_template_list(rule, filtered_files)

            self.files      = []
            self.folders    = []

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

    def generate_file_template_list(self, rule: FileRule, filtered_files: list[File]) -> list[MoveToken]:
        template_list: list[MoveToken] = []

        for file in filtered_files:
            template_list.append(MoveToken(file.path, rule.destination))

        return template_list

def scandir(folder: str) -> Tuple[list[File], list[Folder]]:
    '''
    Scan a directory, return a tuple of scanned files and folders
    '''
    files = os.scandir(os.path.expanduser(folder))
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
    '''
    Move files and folders according to the list of MoveTokens.\n
    Will automatically rename duplicates.\n
    Will automatically create a folder if it doesn't exist.
    '''
    for move_token in move_token_list:
        move_token.source = check_and_rename_dupes(move_token.source, move_token.destination)
        if not os.path.exists(move_token.destination):
            os.makedirs(move_token.destination)
        try:
            shutil.move(move_token.source, move_token.destination)
            print(f"moved: {move_token.destination} <-- {move_token.source}")

        except Exception as error:
            print(f"Move failed: {error}")

def filter_if_has_fallback(folder_templates: list[FolderTemplate]) -> list[FolderTemplate]:
    '''We only want FolderTemplates if they contain a folder to put files to.'''
    return filter(lambda folder_template: folder_template.place_for_unwanted is not None, folder_templates)

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
    if extensions is not None or key_words is not None:
        return FileRule(
            key_words,
            extensions,
            destination,
            whitelist,
        )
    else:
        # TODO Raise exception
        print("You must provide at least a list of extensions or a list of key words!")

def check_and_rename_dupes(source: str, destination: str) -> str:
    '''
        Check if file exists at desination, if so, rename file and return string of new filename (path included)
        needs refactoring
    '''
    old_file = source
    (path, file_name) = os.path.split(source)
    potential_destination = os.path.join(destination, file_name)
    file_exists = os.path.isfile(potential_destination)

    if not file_exists:
        return source

    generation = 1
    (file_name, extension) = os.path.splitext(os.path.basename(file_name))

    while file_exists:
        new_file_name = f"{file_name} ({generation}){extension}"
        potential_destination = os.path.join(destination, new_file_name)
        file_exists = os.path.isfile(potential_destination)
        generation += 1

    print(f"Renamed duplicate file: {potential_destination}")
    new_source_file_name = os.path.join(path,new_file_name)
    os.rename(old_file, new_source_file_name)
    return potential_destination

def main():
    sources = ["~/Downloads", "~/Pictures"]
    rules: list[FileRule] = [
        create_file_rule("~/Downloads/Compressed", extensions=["zip", "7z", "tar", "bz2", "rar","xz","gz"]),
        create_file_rule("~/Downloads/Compressed/Java", extensions=["jar"]),
        create_file_rule("~/Downloads/Programs", extensions=["exe","elf","bin","deb", "rpm","msi","appimage"]),
        create_file_rule("~/Downloads/Music", extensions=["mp3","mp2","wav","ogg","aac","flac","alac","dsd","mqa","m4a"]),
        create_file_rule("~/Downloads/Music/midi", extensions=["mid"]),
        create_file_rule("~/Pictures/wallpaper", extensions=["jpeg", "jpg", "png"], key_words=["wallpaper", "unsplash"]),
        create_file_rule("~/Pictures/Screenshot", key_words=["screenshot"]),
        create_file_rule("~/Downloads/Misc/No extensions", extensions=[""]),
        create_file_rule("~/Downloads/Video", extensions=["mp4","mkv"])
        # create_file_rule("~/Downloads/Compressed", extensions=["zip"]),

    ]  
    operations = FileOperations(
        source = sources,
        rules = rules
    )
    folder_gen = [
        FolderTemplate(
            "~/tmp/Downloads",
            [
                "Compressed",
                "Documents", 
                "Pictures", 
                "Music", 
                "Video",
                "Programs",
                "Misc", 
                "Misc/Unsorted", 
                "Misc/No extensions",
                 "Misc/Folders"
            ], 
            "~/tmp/Downloads/Folders"),
        # FolderTemplate("~/tmp/Pictures", ["Wallpaper", "Screenshot", "Art"], "~/Pictures/Misc"),
    ]
    config = Config(
        folder_templates = folder_gen,
        file_operations = [operations]
    )
    # generate_folders(folder_gen)
    config.export("./epic_config.json")

    enforcer = Enforcer(config)
    enforcer.generate_folders()
    enforcer.sort_folders()
    # move(enforcer.move_tokens)
    # enforcer.sort_files()

    # move(enforcer.move_tokens)
    # print(json.dumps([operations, operations], indent = 4, default=lambda o: o.__dict__))
    for s in enforcer.move_tokens:
        print(f"{s.destination} <-- \"{s.source}\"")



if __name__ == "__main__":
    main()