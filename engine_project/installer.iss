; Inno Setup script example
[Setup]
AppName=GenericRuntime
AppVersion=1.0.0
DefaultDirName={autopf}\GenericRuntime
DefaultGroupName=GenericRuntime
OutputBaseFilename=GenericRuntimeInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\GenericRuntime\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\GenericRuntime (GUI)"; Filename: "{app}\GenericRuntime.exe"; Parameters: "--mode gui"
Name: "{group}\GenericRuntime (Headless)"; Filename: "{app}\GenericRuntime.exe"; Parameters: "--mode headless"
