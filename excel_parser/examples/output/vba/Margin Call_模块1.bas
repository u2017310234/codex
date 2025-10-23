Attribute VB_Name = "模块1"
Sub Margin_Call()
Attribute Margin_Call.VB_ProcData.VB_Invoke_Func = " \n14"

'   Step 1: input today's date in A1 of this workbook
    Dim datet As Integer
    datet = ThisWorkbook.A1.Value

'   Copy the file to the folder named with today's date
    ActiveWorkbook.SaveAs Filename:= _
    "credit/" & datet & "raw/" & a & datet & ".xlsx" _
    , FileFormat:=xlOpenXMLWorkbook, CreateBackup:=False
    
    For i = 1 To lngLastRow
        iPos = InStrRev(Range("A" & i), ".")
        FileCopy Range("A" & i), "C:\" & Range("B" & i) & Mid(Range("A" & i), iPos, Len(Range("A" & i)))
    Next i

'   Insert Cells and Input Formula Automatively
    With Workbook(".xlsx")
        With .Sheet1
        'Attention! Examine the sheet's code in VBA:
        .Rows(1).Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
        .Colums("AL:AL").Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove
        .Colums("AM:AM").Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove
        
        'Input Formula
        Range("AL2:AL12").FormulaR1C1 = "=1+1+2"
        End With
    End With
    
'   order

'   vlookup

'   If different currency

'   tick


    
    'supervision tablet 监查表
    Dim lngLastRow As Integer
    lngLastRow = Range("A" & Rows.Count).End(xlUp).Row
    
    Rows("1:1").Select
    Selection.Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
    ActiveWindow.ScrollColumn = 2
    Columns("AL:AL").Select
    Selection.Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
    Columns("AM:AM").Select
    Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove
    ActiveWindow.ScrollColumn = 28
    ActiveWindow.ScrollColumn = 27
    ActiveWindow.ScrollColumn = 26
    ActiveWindow.ScrollColumn = 25
    ActiveWindow.ScrollColumn = 24
    ActiveWindow.ScrollColumn = 23
    ActiveWindow.ScrollColumn = 22
    ActiveWindow.ScrollColumn = 20
    ActiveWindow.ScrollColumn = 18
    ActiveWindow.ScrollColumn = 16
    ActiveWindow.ScrollColumn = 13
    ActiveWindow.ScrollColumn = 10
    ActiveWindow.ScrollColumn = 7
    ActiveWindow.ScrollColumn = 4
    ActiveWindow.ScrollColumn = 2
    ActiveWindow.ScrollColumn = 1
    Range("E1").Select
    ActiveCell.FormulaR1C1 = "=1+1+2"
    Range("E2").Select
    ActiveWindow.ScrollColumn = 2
    Range("P3").Select
    ActiveCell.Formula2R1C1 = "=a+b"
    Range("P4").Select
    ChDir "E:\3-实习\OneDrive - connect.hku.hk\平安证券"
    ActiveWorkbook.SaveAs Filename:= _
        "https://connecthkuhk-my.sharepoint.com/personal/u3588064_connect_hku_hk/Documents/平安证券/Margin%20Call.xlsx" _
        , FileFormat:=xlOpenXMLWorkbook, CreateBackup:=False
    ActiveWorkbook.SaveAs Filename:= _
        "https://connecthkuhk-my.sharepoint.com/personal/u3588064_connect_hku_hk/Documents/平安证券/Margin%20Call.xlsm" _
        , FileFormat:=xlOpenXMLWorkbookMacroEnabled, CreateBackup:=False
End Sub
Sub 宏2()
Attribute 宏2.VB_ProcData.VB_Invoke_Func = " \n14"
'
' 宏2 宏
'

'
    Windows("Credit Risk vJune2022.xlsm").Activate
    Selection.Copy
    Windows("Margin Call.xlsm").Activate
    Range("I7").Select
    Application.CutCopyMode = False
    ActiveCell.FormulaR1C1 = "1"
    Columns("I:I").Select
    Range("I7").Activate
    Windows("Credit Risk vJune2022.xlsm").Activate
    Selection.Copy
    Windows("Margin Call.xlsm").Activate
    ActiveSheet.Paste
End Sub
