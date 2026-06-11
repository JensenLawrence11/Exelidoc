; Office AI Add-in Installer
; Build with: makensis office-ai-addin.nsi

!include "MUI2.nsh"
!include "x64.nsh"

; ─── Settings ──────────────────────────────────────────────────────────────────

Name "Office AI Add-in"
OutFile "Exelidoc-Installer.exe"
InstallDir "$PROGRAMFILES\Office AI"
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
    CreateDirectory "$SMPROGRAMS\Office AI"
    CreateShortcut "$SMPROGRAMS\Office AI\Office AI Control Panel.lnk" \
        "$INSTDIR\Exelidoc.exe" "" "$INSTDIR\Exelidoc.exe" 0
    CreateShortcut "$DESKTOP\Office AI Control Panel.lnk" \
        "$INSTDIR\Exelidoc.exe" "" "$INSTDIR\Exelidoc.exe" 0
    
    ; Register manifest with Office (optional, advanced)
    ; This would require VBScript to add to trusted locations
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    CreateShortcut "$SMPROGRAMS\Office AI\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
SectionEnd

; ─── Uninstallation ───────────────────────────────────────────────────────────

Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\Office AI"
    Delete "$DESKTOP\Office AI Control Panel.lnk"
SectionEnd
