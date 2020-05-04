Public Class Prefill
  Inherits ESRI.ArcGIS.Desktop.AddIns.Button
    Private _frmTest As frmTest

  Public Sub New()

  End Sub

  Protected Overrides Sub OnClick()
        Try
            'Execute Prefill Python Script
            ExecutePythonTool("Prefill")

        Catch ex As Exception
            LogError(ex, True)
        End Try
  End Sub

  Protected Overrides Sub OnUpdate()

  End Sub
End Class
