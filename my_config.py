#! /usr/bin/python
# My custom configuration.

from main import Config, Operation, FolderTemplate, create_file_rule
import constants as const

#----------------------------------------------------------------------------------------------

DEFAULT_FOLDERS = [
    FolderTemplate(
        "~/Downloads",
        [
            "Compressed",
            "Documents",
            "Documents/Word",
            "Documents/txt",
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
            "Programs/Jupyter Notebook",
            "Programs/Android",
            "Programs/Sql",
            "Programs/Python Libraries",
            "Programs/Scratch",
            "Programs/DLL",

            "Folders",
            "Disk Images",
            "Torrents",
            "Torrents/Linux",
            "Torrents/Magnets",

            "Misc",
            "Misc/Valve stuff",
            "Misc/No extension",
            "Misc/Fonts",
            "Misc/Anki",
            "Misc/Bookmarks",
            "Misc/Excalidraw",
            "Misc/LMMS Projects",
            "Misc/LMMS Presets",
            "Misc/Krita Projects",
            "Misc/SoundFonts",
            "Misc/Paint NET Projects",
            "Misc/Flash",
            "Unsorted",
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

SORT_DOWNLOADS = Operation(
    ["~/Downloads", "~/Downloads/Unsorted"],
    [
        create_file_rule("~/Downloads/Compressed",          const.ARCHIVES),
        create_file_rule("~/Downloads/Documents/Word",      ["docx"]),
        create_file_rule("~/Downloads/Documents/Pdf",       ["pdf"]),
        create_file_rule("~/Downloads/Documents/Ebook",     ["epub"]),
        create_file_rule("~/Downloads/Documents/txt",       ["txt"]),
        create_file_rule("~/Downloads/Documents/RSS",       extensions=["rss", "atom"]),

        create_file_rule("~/Downloads/Pictures",            const.IMAGE),
        create_file_rule("~/Downloads/Pictures/Vector",     ["svg"]),

        create_file_rule("~/Downloads/Music",               const.AUDIO),
        create_file_rule("~/Downloads/Music/Tracker",       ["it","mod","xm","s3m","umx", "mptm"]),
        create_file_rule("~/Downloads/Music/midi",          extensions=["mid"]),

        create_file_rule("~/Downloads/Video",               const.VIDEO),

        create_file_rule("~/Downloads/Programs",            extensions=["exe", "deb", "msi", "appimage", "AppImage","msu", "appinstaller", "flatpak"]),
        create_file_rule("~/Downloads/Programs/Python",     extensions=["py"]),
        create_file_rule("~/Downloads/Programs/Shell",      extensions=["sh", "ps1"]),
        create_file_rule("~/Downloads/Programs/Jupyter Notebook",   extensions=["ipynb"]),
        create_file_rule("~/Downloads/Programs/Python Libraries",   extensions=["whl"]),
        create_file_rule("~/Downloads/Programs/DLL",                extensions=["dll"]),
        create_file_rule("~/Downloads/Programs/Scratch", extensions=["sb", "sb2", "sb3"]),


        create_file_rule("~/Downloads/Torrents/Linux", keywords=["linux"], extensions=["torrent"]),
        create_file_rule("~/Downloads/Torrents", extensions=["torrent"]),
        create_file_rule("~/Downloads/Torrents/Magnets", extensions=["magnet"]),
        
        create_file_rule("~/Downloads/Disk Images",         extensions=["iso", "img"]),

        create_file_rule("~/Downloads/Misc/Valve stuff",    extensions=["vtf", "vpk"]),
        create_file_rule("~/Downloads/Misc/Anki",           extensions=["apkg"]),
        create_file_rule("~/Downloads/Misc/Bookmarks",      keywords=["bookmark"], extensions=["html", "json"]),
        create_file_rule("~/Downloads/Misc/Excalidraw",     extensions=["excalidraw", "drawio"]),
        create_file_rule("~/Downloads/Misc/Fonts",          extensions=["ttf","woff2","woff"]),
        create_file_rule("~/Downloads/Misc/LMMS Projects",  extensions=["mmpz", "mmp"]),
        create_file_rule("~/Downloads/Misc/LMMS Presets",   extensions=["xpf", "xpt", "xptz"]),
        create_file_rule("~/Downloads/Misc/Krita Projects", extensions=["kra"]),
        create_file_rule("~/Downloads/Misc/Paint NET Projects", extensions=["pdn"]),
        create_file_rule("~/Downloads/Misc/SoundFonts", extensions=["sf2","sf3", "sfz"]),
        create_file_rule("~/Downloads/Misc/Flash", extensions=["swf"]),
    ]
)

SORT_PICTURES = Operation(
    ["~/Pictures","~/Downloads/Pictures","~/Downloads"],
    [
        create_file_rule("~/Pictures/Screenshots", keywords=["screenshot"]),
        create_file_rule("~/Pictures/Wallpapers", keywords=["wallpaper", "unsplash", "pexels", "wallhaven", "1920x1080", "4k"])
    ]
)

SORT_TORRENTS = Operation(
    ["~/Downloads/Torrents"],
    [
        create_file_rule("~/Downloads/Torrents/Linux", keywords=["linux", "ubuntu"], extensions=["torrent"]),
        create_file_rule("~/Downloads/Torrents/Archive", keywords=["archive", "ubuntu"], extensions=["torrent", "magnet"]),
    ]
)

# We may have some files after a cleanup, move them to the unsorted folder.
# NOTE: Do not merge with the operation above, this can create a cylce.
SORT_RESIDUAL_FILES = Operation(
    ["~/Downloads"],
    [create_file_rule("~/Downloads/Unsorted/", keywords="")]
)

#----------------------------------------------------------------------------------------------

DEFAULT_CONFIG: Config = Config(
    DEFAULT_FOLDERS,
    [
        SORT_PICTURES,
        SORT_DOWNLOADS,
        SORT_TORRENTS,
        SORT_RESIDUAL_FILES # Must be placed last or can create a cycle
    ]
)

#----------------------------------------------------------------------------------------------

if __name__ == "__main__":
    DEFAULT_CONFIG.export("./configs/B0ney_config.json")
