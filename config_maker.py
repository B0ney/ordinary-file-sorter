# I might make a gui app that does this.

from main import Config, Operation, FolderTemplate, create_file_rule
import constants as const

#----------------------------------------------------------------------------------------------

DEFAULT_FOLDERS: list[FolderTemplate] = [
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
            "Folders",
            "Misc",
            "Misc/No extension",
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
        create_file_rule("~/Downloads/Compressed", const.ARCHIVES),
        create_file_rule("~/Downloads/Documents", const.DOCS),
        create_file_rule("~/Downloads/Pictures", const.IMAGE),
        create_file_rule("~/Downloads/Music",   const.AUDIO),
        create_file_rule("~/Downloads/Video",   const.VIDEO),
        create_file_rule("~/Downloads/Programs", const.PROGRAMS),
        create_file_rule("~/Downloads/Misc/No extension", extensions=""),
    ]
)

SORT_PICTURES: Operation = Operation(
    ["~/Pictures","~/Downloads/Pictures"],
    [
        create_file_rule("~/Pictures/Screenshots",  keywords=["screenshot"]),
        create_file_rule("~/Pictures/Wallpapers",   keywords=["wallpaper","unsplash"])
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
        DEFAULT_OPERATION,
        SORT_PICTURES,
        SORT_RESIDUAL_FILES # Must be placed last or can create a cycle
    ]
)

#----------------------------------------------------------------------------------------------

if __name__ == "__main__":
    DEFAULT_CONFIG.export("./configs/default.json")
