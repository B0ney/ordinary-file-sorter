import re
import os.path
import shutil
import json 
from typing import Tuple

class Folder():
    def __init__(self, name: str, path: str):
        self.name           = name
        self.path           = path

class File():
    def __init__(self, name: str, extension: str, path: str):
        self.name           = name
        self.extension      = extension
        self.path           = path
        
class FileRule():
    def __init__(self, key_words: list[str], extensions: list[str], destination: str, whitelist: list[str] = None):
        self.key_words      = key_words
        self.extensions     = extensions
        self.destination    = destination
        self.whitelist      = whitelist

class  MoveToken():
    def __init__(self, source: str, destination: str):
        self.source         = source
        self.destination    = destination

class FolderTemplate():
    def __init__(self, root_folder: str, folders: list[str], unknown_folder: str = None):
        self.root_folder    = root_folder
        self.folders        = folders
        self.place_for_unwanted = unknown_folder

    def as_iter(self) -> list[str]: # too much rust influence
        # spits out a list of folders with their raw path
        return map(lambda folder: os.path.join(self.root_folder, folder), self.folders)

class FileOperations():
    def __init__(self, source: list[str], rules: list[FileRule]):
        self.sources    = source
        self.rules      = rules
        
class Config():
    def __init__(self, folder_templates: list[FolderTemplate] = None, file_operations: list[FileOperations] = None):
        self.folder_templates   = folder_templates
        self.file_operations    = file_operations

    def export(self, file_path: str):
        # TODO: add error handling
        out_file = open(file_path, "w")
        json.dump(self, out_file, indent = 4, default=lambda o: o.__dict__)
        out_file.close()

    def load(self, file_path: str):
        pass

class Enforcer():
    def __init__(self, config: Config):
        self.config:            Config          = config
        self.move_tokens:       list[MoveToken] = []
        self.files:             list[File]      = []
        self.folders:           list[Folder]    = []
        self.scanned_sources:   list[File]      = []
    
    def generate_folders(self):
        # Perfect, no need to refactor
        for folder_template in self.config.folder_templates:
            for folder in folder_template.as_iter():      
                if not os.path.exists(folder):
                    try:
                        os.makedirs(folder)
                        print(f"INFO: Created folder: '{folder}'")

                    except Exception as e:
                        print(f"WARN: Could not create folder: '{folder}', {e}")
                else:
                    print(f"INFO: Ignored folder (Already exists): '{folder}'.")

    def sort_folders(self):
        template_with_fallback = filter_if_has_fallback(self.config.folder_templates)
        move_tokens: list[MoveToken] = []

        for folder_template in template_with_fallback:
            (_, scanned_folders) = scandir(folder_template.root_folder)
            
            for folder in scanned_folders:
                unhandled_files_dir = folder_template.place_for_unwanted

                if folder.name not in folder_template.folders and folder.path != os.path.expanduser(unhandled_files_dir):
                    move_tokens.append(MoveToken(folder.path, unhandled_files_dir))

        self.move_tokens += move_tokens
            
    def sort_files(self):
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
        # A user can choose to scan multiple folders before enforcing a rule(s)
        # Scanned folders will add data to the files list
        if path in self.scanned_sources:
            print(f"WARN: Scanning operation ignored: Source '{path}' already scanned")
        else:
            (scanned_files, _) = scandir(path)
            self.files += scanned_files
            self.scanned_sources.append(path)

            print(f"INFO: Scanned {path}. {len(scanned_files)} files scanned")

    def filter_files(self, rule: FileRule) -> list[File]:
        # Filtering order: whitelist -> file extension -> key words
        filtered_files: list[File] = self.files

        if rule.whitelist != None:
            filtered_files = filter_by_whitelist(filtered_files, rule.whitelist)

        if rule.extensions != None:
            filtered_files = filter_by_extension(filtered_files, rule.extensions)

        if rule.key_words != None:
            filtered_files = filter_by_key_word(filtered_files, rule.key_words)

        return filtered_files

    def generate_file_template_list(self, rule: FileRule, filtered_files: list[File]) -> list[MoveToken]:
        template_list: list[MoveToken] = []

        for file in filtered_files:
            template_list.append(MoveToken(file.path, rule.destination))

        return template_list

def scandir(folder: str) -> Tuple[list[File], list[Folder]]:
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
    for move_token in move_token_list:
        (_, file_name) = os.path.split(move_token.source)
        destination_path = os.path.expanduser(os.path.join(move_token.destination, file_name))
        
        if os.path.isfile(destination_path):
            print(f"WARN: File {file_name} already exists!")
        else:
            try:
                # shutil.move(move_token.source, move_token.destination)
                print(f"moved: {move_token.destination} <-- {move_token.source}")

            except Exception as error:
                print(f"Move failed: {error}")

def filter_if_has_fallback(folder_templates: list[FolderTemplate]) -> list[FolderTemplate]:
    '''We only want FolderTemplates if they contain a folder to put files to.'''
    return filter(lambda folder_template: folder_template.place_for_unwanted != None, folder_templates)

def filter_by_whitelist(list_of_files: list[File], whitelist: list[str]) -> list[File]:
    # Return an iterator of non whitelisted Files 
    return filter(lambda file: file.name not in whitelist, list_of_files)

def filter_by_extension(list_of_files: list[File], extensions: list[str]) -> list[File]:
    # Return an iterator that yields File objects such that their extensions are in a list 
    return filter(lambda file: file.extension in map(lambda ext: ext.strip("."), extensions), list_of_files)

def filter_by_key_word(list_of_files: list[File], words: list[str]) -> list[File]:
    # Return an iterator of Files if their filenames satisfy a particluar word
    return filter(lambda file: re.search(as_regex(words), file.name.lower()), list_of_files)

def as_regex(list_of_key_words: list[str]) -> str:
    # TODO sanitise words in list to get rid of special characters
    return f"{'|'.join(list_of_key_words)}"

def create_file_rule(destination: str, extensions: list[str] = None, key_words: list[str] = None, whitelist: list[str] = None) -> FileRule:
    if extensions != None or key_words != None:
        return FileRule(
            key_words,
            extensions,
            destination,
            whitelist,
        )
    else:
        # TODO Raise exception
        print("You must provide at least a list of extensions or a list of key words!")

def main():
    sources = ["~/Downloads", "~/Pictures"]
    rules: list[FileRule] = [
        create_file_rule("~/Downloads/Compressed", extensions=["zip", "7z", "tar", "bz2", "rar","xz"]),
        create_file_rule("~/Downloads/Compressed/Java", extensions=["jar"]),
        create_file_rule("~/Download/Programs", extensions=["exe","elf","bin","deb", "rpm","msi","appimage"]),
        create_file_rule("~/Download/Music", extensions=["mp3","mp2","wav","ogg","aac","flac","alac","dsd","mqa"]),
        create_file_rule("~/Download/Music/midi", extensions=["mid"]),
        create_file_rule("~/Pictures/wallpaper", extensions=["jpeg", "jpg", "png"], key_words=["wallpaper", "unsplash"]),
        create_file_rule("~/Pictures/Screenshot", key_words=["screenshot"]),
        create_file_rule("~/Downloads/Misc/No extensions", extensions=[""]),
    ]  
    operations = FileOperations(
        source = sources,
        rules = rules
    )
    folder_gen = [
        FolderTemplate("~/Downloads", ["Compressed", "Documents", "Pictures", "Music", "Video","Programs", "Misc/Unsorted", "Misc/No extensions", "Misc/Folders"], "~/Downloads/Folders"),
        FolderTemplate("~/Pictures", ["Wallpaper", "Screenshot", "Art"], "~/Pictures/Misc"),
    ]
    config = Config(
        folder_templates = folder_gen,
        file_operations = [operations]
    )
    # generate_folders(folder_gen)
    # config.export("./epic_config.json")

    enforcer = Enforcer(config)
    enforcer.sort_folders()
    # enforcer.sort_files()

    move(enforcer.move_tokens)


    # for s in enforcer.move_tokens:
    #     print(f"{s.destination} <-- \"{s.source}\"")



if __name__ == "__main__":
    main()