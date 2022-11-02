# Filename Replace

This is a very simple script to rename generic pronouns in files to proper names after using auto captioning.  This script does not create copies.  It renames the files in place.

By default, it will replace "a man", "a woman", and "a person" with your supplied proper name.  This works well for single subject without tweaking.


## Usage

    python scripts/filename_replace.py --img_dir output --replace "john doe"

*"a man standing in a park with birds on his shoulders.jpg"
-> 
"john doe standing in a park with birds on his shoulders.jpg"*

## Chaining with auto caption

You can chain together the auto_caption.py and file_rename.py to help deal with multiple people in photos in a simple shell script (bash or windows .bat) with a bit of thinking about what you replace and using --find to specify the pronoun to replace first more specifically than all three default pronouns. 

    python scripts/auto_caption.py --q_factor 1.4 --img_dir input --out_dir output 
    python scripts/filename_replace.py --img_dir output --find "a woman" --replace "rihanna" 
    python scripts/filename_replace.py --img_dir output --replace "asap rocky"

"a man and a woman standing next to each other in front of a green wall with leaves on it.webp" 
->
"asap rocky and rihanna standing next to each other in front of a green wall with leaves on it.webp"

See clip_rename.bat in the root folder, modify it to your needs.

Renaming is nearly instant as it is just renaming the files and not using and AI models or calculations, just a dumb find and replace on the filename. 