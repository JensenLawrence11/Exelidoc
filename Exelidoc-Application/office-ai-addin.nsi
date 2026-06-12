; Exelidoc Add-in Installer
; Build with: makensis Exelidoc-addin.nsi

!include "MUI2.nsh"
!include "x64.nsh"

; ─── Settings ──────────────────────────────────────────────────────────────────

Name "Exelidoc Add-in"
OutFile "Exelidoc-Installer.exe"
InstallDir "$PROGRAMFILES\Exelidoc"
RequestExecutionLevel admin

; ─── MUI Settings ──────────────────────────────────────────────────────────────

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; ─── Installation ──────────────────────────────────────────────────────────────

Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy executable and files
    File /r "dist\Exelidoc\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Exelidoc"
    CreateShortcut "$SMPROGRAMS\Exelidoc\Exelidoc Control Panel.lnk" \
        "$INSTDIR\Exelidoc.exe" "" "$INSTDIR\Exelidoc.exe" 0
    CreateShortcut "$DESKTOP\Exelidoc Control Panel.lnk" \
        "$INSTDIR\Exelidoc.exe" "" "$INSTDIR\Exelidoc.exe" 0
    
    ; Register manifest with Office (optional, advanced)
    ; This would require VBScript to add to trusted locations
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    CreateShortcut "$SMPROGRAMS\Exelidoc\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
SectionEnd

; ─── Uninstallation ───────────────────────────────────────────────────────────

Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\Exelidoc"
    Delete "$DESKTOP\Exelidoc Control Panel.lnk"
SectionEnd
