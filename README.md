# Source-code-importer-to-Visual-Studio
This tool imports source code to Visual Studio. Folder structure is preserved during importing.


Usage: <file>.py <source code absolute path> <output directory absolute path> <project name> filter( <file type>;<file type>... )
  
Source code absolute path - ex. C:\83.0.4103.61_build
Output directory absolute path - ex. C:\gen
Project name - Valid filename
Filter - All file type that will be included during importing. This is ; separated ex. cpp;c;cc;h, use .* or *.* to include all.

Solution file .sln is create on output directory after importing.
Open .sln file in Visual Studio.
