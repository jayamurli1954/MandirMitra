; MandirSync Installer Script for Inno Setup
; Compile this with Inno Setup Compiler to create MandirSync-Setup.exe

#define AppName "MandirSync"
#define AppVersion "1.0.0"
#define AppPublisher "MandirSync"
#define AppURL "https://mandirsync.com"
#define AppExeName "MandirSync-Launcher.exe"
#define InstallDir "{user}\MandirSync"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={#InstallDir}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=MandirSync-Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "MandirSync-Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALLATION_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
; Note: Add backend and frontend source files here if including in installer
; Source: "..\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "..\frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to the MandirSync Setup Wizard';
  WizardForm.WelcomeLabel2.Caption := 'This wizard will guide you through the installation of MandirSync v1.0.' + #13#10 + #13#10 +
    'MandirSync is a comprehensive temple management system.' + #13#10 + #13#10 +
    'Click Next to continue.';
end;

function InitializeSetup(): Boolean;
var
  PythonVersion: String;
  NodeVersion: String;
  PostgreSQLVersion: String;
  ResultCode: Integer;
begin
  Result := True;
  
  // Check Python
  if not Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if MsgBox('Python 3.11+ is required but not found. Do you want to continue anyway?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
  
  // Check Node.js
  if not Exec('node', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if MsgBox('Node.js 18+ is required but not found. Do you want to continue anyway?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
  
  // Check PostgreSQL
  if not Exec('psql', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if MsgBox('PostgreSQL 14+ is required but not found. Do you want to continue anyway?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

