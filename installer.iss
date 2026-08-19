#define MyAppName "ÇiftlikPro Enterprise"
#define MyAppVersion "3.9.2"
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
OutputBaseFilename=CiftlikPro_Enterprise_V3_7_3_Lisans_Key_Aktivasyonu_Setup
SetupIconFile=CiftlikPro.ico
UninstallDisplayIcon={app}\CiftlikPro.exe
PrivilegesRequired=admin
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
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""ÇiftlikPro LAN 8953"""; Flags: runhidden waituntilterminated
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall add rule name=""ÇiftlikPro LAN 8953"" dir=in action=allow protocol=TCP localport=8953 profile=any"; Flags: runhidden waituntilterminated
Filename: "{app}\CiftlikPro.exe"; Description: "ÇiftlikPro'yu başlat"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""ÇiftlikPro LAN 8953"""; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
