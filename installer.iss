#define MyAppName "ÇiftlikPro Enterprise"
#define MyAppVersion "2.1.0-beta1-edit-hotfix"
#define MyAppPublisher "ÇiftlikPro"
#define MyAppExeName "CiftlikPro.exe"

[Setup]
AppId={{D24FAAC2-226C-47A9-B0FB-B65D6575EFC8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\CiftlikPro
DefaultGroupName=ÇiftlikPro
OutputDir=release
OutputBaseFilename=CiftlikPro_Enterprise_V2_1_Beta1_EditHotfix_Setup
SetupIconFile=CiftlikPro.ico
UninstallDisplayIcon={app}\CiftlikPro.exe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Files]
Source: "dist\CiftlikPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\ÇiftlikPro"; Filename: "{app}\CiftlikPro.exe"; WorkingDir: "{app}"
Name: "{userprograms}\ÇiftlikPro"; Filename: "{app}\CiftlikPro.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\CiftlikPro.exe"; Description: "ÇiftlikPro'yu başlat"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
