# Source-code-importer-to-Visual-Studio
This tool imports source code to Visual Studio. Folder structure is preserved during importing.


Usage: [file.py] [source code absolute path] [output directory absolute path] [project name] [filter file type;file type...]
  
Sample: 
  
python import.py C:\83.0.4103.61_build C:\gen Project_1 \*.\*

python import.py C:\83.0.4103.61_build C:\gen Project_1 cc;cpp;h;c

Solution file(.sln) is created on output directory after importing.
Open .sln file in Visual Studio.
