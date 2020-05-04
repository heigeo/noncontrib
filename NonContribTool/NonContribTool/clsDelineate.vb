Public Class clsDelineate
  Inherits ESRI.ArcGIS.Desktop.AddIns.Button

  Public Sub New()

  End Sub

  Protected Overrides Sub OnClick()
        Try
            'Execute Express Calc Python Script
            ExecutePythonTool("delineatewshd")
        Catch ex As Exception
            LogError(ex, True)
        End Try
  End Sub

  Protected Overrides Sub OnUpdate()

  End Sub
End Class
