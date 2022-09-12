#! /usr/bin/python
# My custom configuration.

from main import Config, Operation, FolderTemplate, create_file_rule
import constants as const

#----------------------------------------------------------------------------------------------

DEFAULT_FOLDERS: list[FolderTemplate] = [
    FolderTemplate(
        "~/Downloads",
        [
            "Compressed",
            "Documents",
            "Documents/Word",
            "Documents/Pdf",
            "Documents/Ebook",
            "Documents/RSS",
            "Pictures",
            "Pictures/Vector",
            "Music",
            "Music/midi",
            "Music/Tracker",
            "Video",
            "Programs",
            "Programs/Java",
            "Programs/Shell",
            "Programs/Python",
            "Unsorted",
            "Folders",
            "Disk Images",
            "Torrents",
            "Torrents/Magnets",
            "Misc",
            "Misc/Valve stuff",
            "Misc/No extension",
            "Misc/Fonts",
            "Misc/Anki",
            "Misc/Bookmarks",
            "Misc/Excalidraw",
            "Misc/Lmms Projects",
        ],
        place_for_unwanted = "~/Downloads/Folders"
    ),
    FolderTemplate(
        "~/Pictures",
        [
            "Screenshots",
            "Wallpapers"
        ]
    )
]

#----------------------------------------------------------------------------------------------

DEFAULT_OPERATION: Operation = Operation(
    ["~/Downloads", "~/Downloads/Unsorted"],
    [
        create_file_rule("~/Downloads/Compressed",          const.ARCHIVES),
        create_file_rule("~/Downloads/Documents/Word",      ["docx"]),
        create_file_rule("~/Downloads/Documents/Pdf",       ["pdf"]),
        create_file_rule("~/Downloads/Documents/Ebook",     ["epub"]),
        create_file_rule("~/Downloads/Documents",           ["txt"]),
        create_file_rule("~/Downloads/Documents/RSS",       extensions=["rss", "atom"]),

        create_file_rule("~/Downloads/Pictures",            const.IMAGE),
        create_file_rule("~/Downloads/Pictures/Vector",     ["svg"]),

        create_file_rule("~/Downloads/Music",               const.AUDIO),
        create_file_rule("~/Downloads/Music/Tracker",       ["it","mod","xm","s3m"]),
        create_file_rule("~/Downloads/Music/midi",          extensions=["mid"]),
        create_file_rule("~/Downloads/Video",               const.VIDEO),
        create_file_rule("~/Downloads/Programs",            extensions=["exe", "deb", "msi", "appimage", "AppImage"]),
        create_file_rule("~/Downloads/Programs/Java",       extensions=["jar"]),
        create_file_rule("~/Downloads/Programs/Python",     extensions=["py"]),
        create_file_rule("~/Downloads/Programs/Shell",      extensions=["sh"]),
        create_file_rule("~/Downloads/Torrents",            extensions=["torrent"]),
        create_file_rule("~/Downloads/Torrents/Magnets",    extensions=["magnet"]),
        create_file_rule("~/Downloads/Disk Images",         extensions=["iso", "img"]),

        create_file_rule("~/Downloads/Misc/Valve stuff",    extensions=["vtf", "vpk"]),
        create_file_rule("~/Downloads/Misc/Anki",           extensions=["apkg"]),
        create_file_rule("~/Downloads/Misc/Bookmarks",      keywords=["bookmarks"], extensions=["html", "json"]),
        create_file_rule("~/Downloads/Misc/Excalidraw",     extensions=["excalidraw"]),
        create_file_rule("~/Downloads/Misc/Fonts",          extensions=["ttf"]),
        create_file_rule("~/Downloads/Misc/Lmms Projects",  extensions=["mmpz", "mmp"]),


        create_file_rule("~/Downloads/Misc/No extension",   extensions=""),
    ]
)

SORT_PICTURES: Operation = Operation(
    ["~/Pictures","~/Downloads/Pictures","~/Downloads"],
    [
        create_file_rule("~/Pictures/Screenshots",  keywords=["screenshot"]),
        create_file_rule("~/Pictures/Wallpapers",   keywords=["wallpaper","unsplash", "pexels", "wallhaven", "1920x1080", "4k"])
    ]
)

# We may have some files after a cleanup, move them to the unsorted folder.
# NOTE: Do not merge with the operation above, this can create a cylce.
SORT_RESIDUAL_FILES: Operation = Operation(
    ["~/Downloads"],
    [create_file_rule("~/Downloads/Unsorted/", keywords="")]
)

#----------------------------------------------------------------------------------------------

DEFAULT_CONFIG: Config = Config(
    DEFAULT_FOLDERS,
    [
        SORT_PICTURES,
        DEFAULT_OPERATION,
        SORT_RESIDUAL_FILES # Must be placed last or can create a cycle
    ]
)

#----------------------------------------------------------------------------------------------

if __name__ == "__main__":
    DEFAULT_CONFIG.export("./configs/B0ney_config.json")
