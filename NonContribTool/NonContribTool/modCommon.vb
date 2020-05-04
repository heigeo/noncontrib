Imports System.IO
Imports ESRI.ArcGIS.Geoprocessing
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.GeoprocessingUI

Module modCommon
    'Constants
    Public Const MSG_TITLE As String = "Non-Contributing Analysis"
    Private Const MAX_LOG_BYTES As Integer = 10000000 'limit logs to 10 megs
    Private Const ERR_LOG_FILE_NAME As String = "ERROR_LOG.txt"

    Friend Sub LogError(ByVal ex As Exception, Optional ByVal ShowMessage As Boolean = False, Optional ByVal AlternateMessage As String = "")
        '******************************************************************************
        '* This sub logs errors and the stack trace for each.
        '* The size of the log is limited to MAX_LOG_BYTES.  If the file or the directory
        '* does not exist, this sub will attemp to create them.
        '******************************************************************************
        Try
            'Dim errLogPath2 As String = My.Application.Info.DirectoryPath & "\LOG\" & ERR_LOG_FILE_NAME
            Dim errLogPath As String = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) & "\LOG\" & ERR_LOG_FILE_NAME

            Dim bCreate As Boolean
            If Not System.IO.File.Exists(errLogPath) Then
                Dim sDir As String = System.IO.Path.GetDirectoryName(errLogPath)
                If Not Directory.Exists(sDir) Then
                    Directory.CreateDirectory(sDir)
                End If
                bCreate = True
            Else
                If My.Computer.FileSystem.GetFileInfo(errLogPath).Length > MAX_LOG_BYTES Then
                    bCreate = True
                End If
            End If
            If bCreate Then
                Using fStream As System.IO.FileStream = File.Create(errLogPath)
                End Using
            End If

            Dim sOut As String

            sOut = DateTime.Now.ToShortDateString & " " & DateTime.Now.ToLongTimeString() & vbNewLine & _
                   "Error Message: " & ex.Message & vbNewLine & _
                   "Stack Trace: " & vbNewLine & ex.StackTrace & vbNewLine

            Using writer As StreamWriter = File.AppendText(errLogPath)
                With writer
                    .WriteLine("{0}", sOut)
                    .WriteLine("------------------------------------------------")
                    .WriteLine(vbTab)
                    ' Update the underlying file.
                    .Flush()
                End With
            End Using
        Catch exc As Exception
        End Try

        Try
            If ShowMessage Then
                If AlternateMessage = "" Then
                    MsgBox(ex.Message, MsgBoxStyle.Critical, "Non-Contributing Toolbar Error")
                Else
                    MsgBox(AlternateMessage, MsgBoxStyle.Critical, "Non-Contributing Toolbar Error")
                End If
            End If
        Catch exc1 As Exception
        End Try
    End Sub

    Friend Sub ExecutePythonTool(ByVal strTool As String)
        Try
            'Set a reference to the IGPCommandHelper2 interface.
            Dim pToolHelper As IGPToolCommandHelper2 = New GPToolCommandHelper

            'Set the tool you want to invoke.
            Dim toolboxPath = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) & "\NonContrib.tbx"
            'Dim toolboxPath = "C:\Development\NonContrib\NonContrib.tbx"
            pToolHelper.SetToolByName(toolboxPath, strTool)
            'Dim toolboxPath = "<ArcGIS install directory>\ArcToolbox\Toolboxes\Analysis Tools.tbx"
            'pToolHelper.SetToolByName(toolboxPath, "Buffer")

            'Create the messages object to pass to the InvokeModal method.
            Dim msgs As IGPMessages
            msgs = New GPMessages

            'Invoke the tool.
            pToolHelper.InvokeModal(0, Nothing, True, msgs)
            My.ArcMap.Application.CurrentTool = Nothing
        Catch ex As Exception
            LogError(ex, True)
        End Try
    End Sub
End Module
