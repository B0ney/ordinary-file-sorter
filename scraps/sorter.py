from curses.ascii import CR
import glob
import re
import os.path
import shutil

class Criteria():
    def __init__(self, key_words: list[str], extensions: list[str]) -> None:
        self.key_words      = key_words
        self.extensions     = extensions
    
class Rule():
    def __init__(self, criteria: Criteria, destination: str) -> None:
        self.criteria       = criteria
        self.destination    = destination

class File():
    def __init__(self, name: str, extension: str, path: str) -> None:
        self.name           = name
        self.extension      = extension
        self.path           = path
        
class Template():
    def __init__(self, source: str, destination: str) -> None:
        self.source         = source
        self.destination    = destination

class Enforcer():
    def __init__(self):
        self.templates:         list[Template]  = []
        self.files:             list[File]      = []
        self.scanned_sources:   list[File]      = []
        self.rules:             list[Rule]      = []
    
    def scan_folder(self, source: str):
        # A user can choose to scan multiple folders before enforcing a rule(s)
        # Scanned folders will add data to the files list
        if source in self.scanned_sources:
            print(f"Scanning operation ignored: Source '{source}' already scanned")
        else:
            self.files += scandir(source)
            self.scanned_sources.append(source)

    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        print("Rule added")

    def add_rules(self, rules: list[Rule]):
        self.rules += rules
        print(f"{len(rules)} Rules added")

    def enforce(self, rule: Rule):
        # before we can enforce anything, we need to generate a template by filtering out files defined by the rules
        filtered_files = self.filter_files(rule)
        self.templates.append(self.generate_template_list(rule, filtered_files))
        

    def filter_files(self, rule: Rule) -> list[File]:
        filtered_files = self.files

        if self.rule.criteria.extensions != None:
            filter_by_extension(filtered_files, rule.criteria.extensions)

        if self.rule.criteria.key_words != None:
            filter_by_key_word(filtered_files, rule.criteria.key_words)

        return filtered_files

    def generate_template_list(rule: Rule, filtered_files: list[File]) -> list[Template]:
        template_list: list[Template] = []

        for file in filtered_files:
            template_list.push(Template(file.path, rule.destination))

        return template_list

def scandir(folder: str) -> list[File]:
    path = os.path.expanduser(folder)
    files = os.scandir(path)
    scanned_files = []
    for file in files:
        name, extension = os.path.splitext(os.path.basename(file))
        path = os.path.abspath(file)
        scanned_files.append(File(name, extension, path))
        # scanned_files.append("cheese")


    return scanned_files

def move(template_list: list[Template]):
    for template in template_list:
        try:
            shutil.move(template.source, template.destination)
        except Exception as error:
            print(f"Move failed: {error}")

def filter_by_extension(list_of_files: list[File], extensions: list[str]) -> list[File]:
    # Return an iterator that yields File objects such that their extensions are in a list 
    return filter(lambda file: file.extension in extensions, list_of_files)

def filter_by_key_word(list_of_files: list[File], words: list[str]) -> list[File]:
    # Return an iterator of Files if their filenames satisfy a particluar word
    return filter(lambda file: re.match(as_regex(words), file.name.lower()), list_of_files)

def as_regex(list_of_key_words: list[str]) -> str:
    return f"{'|'.join(list_of_key_words)}"

# def add_cases(string: str) -> str:
#     # "test" -> (T|t)est
#     return f"({string[0].upper()}|{string[0].lower()}){string[1:]}"

# def add_bracket(string: str) -> str:
#     return f"({string})"

def main():
    # print(test("hello"))
    # list = ["Wallpaper", "Screenshot"]
    # extensions = ["jpg", "png"]
    # criteria = Criteria(list, extensions)
    # print(criteria.as_regex())
    # regex = r'((S|s)creenshot|(W|w)allpaper)*.png'
    # path = os.path.expanduser("~/Downloads")
    # files = os.scandir(path)
    # files = os.listdir(path)
    enforcer = Enforcer()
    enforcer.scan_folder("~/Downloads")
    
    
    enforcer.scan_folder("~/Pictures")
    # print(enforcer.files)


    for file in enforcer.files:
        print(file.path)


    # test = []
    # for file in files:
    #     name, extension = os.path.splitext(os.path.basename(file))
    #     path = os.path.abspath(file)
    #     test.append(File(name, extension, path))

    # # filtered_ex = filter_by_extension(test, [".zip"])
    # filtered_files = filter_by_key_word(test, ["2021", "wine", "deltarune", "dsk"])

    # for file in filtered_files:
    #     print(f"{file.name}{file.extension}") 
   
    
    pass


if __name__ == "__main__":
    main()