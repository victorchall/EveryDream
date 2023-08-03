# Text Replace Tool

## Overview
The Text Replace Tool is a simple Python application with a graphical user interface (GUI) that allows you to find and replace text strings in all text files within a chosen directory. The application uses the tkinter library for creating the GUI, and the os and re libraries for handling file operations and text replacement.

## Requirements
- Python 3.6 or later

## Installation
1. Download the script `text_replace_tool.py` to your desired folder.
2. Ensure you have Python 3.6 or later installed. You can check your Python version by running `python --version` in your command prompt or terminal.

## Usage
1. Run the script by navigating to the folder containing `text_replace_tool.py` and executing the command `python text_replace_tool.py` in your command prompt or terminal.
2. The Text Replace Tool window will open. Click the "Browse" button to choose the directory containing the text files you want to process.
3. Enter the text you want to find in the "Find:" field, and the text you want to replace it with in the "Replace:" field.
4. Click the "Rename" button to start the text replacement process.
5. A progress bar will show the progress of the operation. Once the process is complete, a "Done" message box will appear.
6. You can either repeat the process for another directory and text strings or close the application.

## Notes
- The application only processes text files with the `.txt` extension.
- Regular expressions are not supported in the find and replace fields. The text entered in these fields will be treated as plain text.
- Ensure you have the necessary permissions to read and write to the chosen directory and the text files within it.

## License
This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).