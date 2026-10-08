#define MyAppName "ÇiftlikPro Enterprise"
#define MyAppVersion "3.9.23 DEV4 Hotfix1.22br"
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
OutputBaseFilename=CiftlikPro_Enterprise_V3_9_23_DEV4_Hotfix1_22bn_Setup
SetupIconFile=CiftlikPro.ico
UninstallDisplayIcon={app}\CiftlikPro.exe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=no
RestartApplications=no

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "autostart"; Description: "Windows açıldığında ÇiftlikPro'yu arka planda başlat"; GroupDescription: "Başlangıç seçenekleri:"; Flags: checkedonce

[Files]
Source: "dist\CiftlikPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\ÇiftlikPro"; Filename: "{app}\CiftlikPro.exe"; WorkingDir: "{app}"
Name: "{userprograms}\ÇiftlikPro"; Filename: "{app}\CiftlikPro.exe"; WorkingDir: "{app}"
Name: "{userstartup}\ÇiftlikPro Arka Plan"; Filename: "{app}\CiftlikPro.exe"; Parameters: "--background"; WorkingDir: "{app}"; Tasks: autostart

[Run]
Filename: "{app}\CiftlikPro.exe"; Description: "ÇiftlikPro'yu başlat"; Flags: nowait postinstall skipifsilent

[UninstallRun]

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  DbFile, BackupDir, BackupFile: String;
begin
  Result := '';
  { Önce normal kapanmayı, ardından yalnız gerekirse zorla sonlandırmayı dene. }
  Exec(ExpandConstant('{cmd}'), '/C taskkill /IM CiftlikPro.exe /T >nul 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(1200);
  Exec(ExpandConstant('{cmd}'), '/C taskkill /F /IM CiftlikPro.exe /T >nul 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(500);

  { Güncelleme öncesi yerel veritabanının geri dönüş kopyası. }
  DbFile := ExpandConstant('{localappdata}\CiftlikPro\ciftlik.db');
  if FileExists(DbFile) then
  begin
    BackupDir := ExpandConstant('{localappdata}\CiftlikPro\backups');
    ForceDirectories(BackupDir);
    BackupFile := BackupDir + '\preinstall_' + GetDateTimeString('yyyymmdd_hhnnss', '-', ':') + '.db';
    if not CopyFile(DbFile, BackupFile, False) then
      Result := 'Kurulum öncesi veritabanı yedeği oluşturulamadı. Kurulum güvenlik amacıyla durduruldu.';
  end;
end;
