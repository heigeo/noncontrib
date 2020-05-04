Public Class Burnlines
    Inherits ESRI.ArcGIS.Desktop.AddIns.Tool
    Private _frmTest As frmTest

    Public Sub New()

    End Sub

    Protected Overrides Sub OnUpdate()

    End Sub

    Protected Overrides Sub OnActivate()
        MyBase.OnActivate()

        MsgBox("The Burnlines tool is not currently being developed!", MsgBoxStyle.Information, MSG_TITLE)
        'System.Windows.Forms.Cursor.Current = Cursors.WaitCursor

        'If _frmTest Is Nothing Then
        '    _frmTest = New frmTest()
        '    _frmTest.Show(New Win32hWndWrapper(CType(My.ArcMap.Application.hWnd, IntPtr)))
        'ElseIf _frmTest.IsDisposed Then
        '    _frmTest = New frmTest()
        '    _frmTest.Show(New Win32hWndWrapper(CType(My.ArcMap.Application.hWnd, IntPtr)))
        'Else
        '    If Not _frmTest.Visible Then
        '        _frmTest.Show(New Win32hWndWrapper(CType(My.ArcMap.Application.hWnd, IntPtr)))
        '    ElseIf _frmTest.WindowState = Windows.Forms.FormWindowState.Minimized Then
        '        _frmTest.WindowState = Windows.Forms.FormWindowState.Normal
        '    Else
        '        _frmTest.Focus()
        '    End If
        'End If

        'do stuff
        My.ArcMap.Application.CurrentTool = Nothing
    End Sub

    Protected Overrides Sub OnMouseDown(ByVal arg As ESRI.ArcGIS.Desktop.AddIns.Tool.MouseEventArgs)
        MyBase.OnMouseDown(arg)

    End Sub
End Class
