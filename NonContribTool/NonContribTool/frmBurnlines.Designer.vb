<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class frmBurnlines
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.txtBurnItem = New System.Windows.Forms.TextBox()
        Me.txtLength = New System.Windows.Forms.TextBox()
        Me.txtName = New System.Windows.Forms.TextBox()
        Me.lblBurnItem = New System.Windows.Forms.Label()
        Me.lblLength = New System.Windows.Forms.Label()
        Me.lblName = New System.Windows.Forms.Label()
        Me.txtID = New System.Windows.Forms.TextBox()
        Me.lblID = New System.Windows.Forms.Label()
        Me.btnSave = New System.Windows.Forms.Button()
        Me.cboDate = New System.Windows.Forms.ComboBox()
        Me.cboBurnItem2 = New System.Windows.Forms.ComboBox()
        Me.lblDate = New System.Windows.Forms.Label()
        Me.lblBurnItem2 = New System.Windows.Forms.Label()
        Me.SuspendLayout()
        '
        'txtBurnItem
        '
        Me.txtBurnItem.BackColor = System.Drawing.SystemColors.Window
        Me.txtBurnItem.Location = New System.Drawing.Point(141, 104)
        Me.txtBurnItem.Name = "txtBurnItem"
        Me.txtBurnItem.ReadOnly = True
        Me.txtBurnItem.Size = New System.Drawing.Size(232, 20)
        Me.txtBurnItem.TabIndex = 15
        '
        'txtLength
        '
        Me.txtLength.BackColor = System.Drawing.SystemColors.Window
        Me.txtLength.Location = New System.Drawing.Point(141, 72)
        Me.txtLength.Name = "txtLength"
        Me.txtLength.ReadOnly = True
        Me.txtLength.Size = New System.Drawing.Size(232, 20)
        Me.txtLength.TabIndex = 14
        '
        'txtName
        '
        Me.txtName.BackColor = System.Drawing.SystemColors.Window
        Me.txtName.Location = New System.Drawing.Point(141, 41)
        Me.txtName.Name = "txtName"
        Me.txtName.ReadOnly = True
        Me.txtName.Size = New System.Drawing.Size(232, 20)
        Me.txtName.TabIndex = 13
        '
        'lblBurnItem
        '
        Me.lblBurnItem.BackColor = System.Drawing.Color.Gray
        Me.lblBurnItem.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.lblBurnItem.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblBurnItem.ForeColor = System.Drawing.Color.White
        Me.lblBurnItem.Location = New System.Drawing.Point(11, 104)
        Me.lblBurnItem.Name = "lblBurnItem"
        Me.lblBurnItem.Size = New System.Drawing.Size(124, 20)
        Me.lblBurnItem.TabIndex = 8
        Me.lblBurnItem.Text = "Burn Item:"
        Me.lblBurnItem.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
        '
        'lblLength
        '
        Me.lblLength.BackColor = System.Drawing.Color.Gray
        Me.lblLength.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.lblLength.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblLength.ForeColor = System.Drawing.Color.White
        Me.lblLength.Location = New System.Drawing.Point(11, 72)
        Me.lblLength.Name = "lblLength"
        Me.lblLength.Size = New System.Drawing.Size(124, 20)
        Me.lblLength.TabIndex = 11
        Me.lblLength.Text = "Length:"
        Me.lblLength.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
        '
        'lblName
        '
        Me.lblName.BackColor = System.Drawing.Color.Gray
        Me.lblName.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.lblName.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblName.ForeColor = System.Drawing.Color.White
        Me.lblName.Location = New System.Drawing.Point(11, 41)
        Me.lblName.Name = "lblName"
        Me.lblName.Size = New System.Drawing.Size(124, 20)
        Me.lblName.TabIndex = 10
        Me.lblName.Text = "Name:"
        Me.lblName.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
        '
        'txtID
        '
        Me.txtID.BackColor = System.Drawing.SystemColors.Window
        Me.txtID.Location = New System.Drawing.Point(141, 12)
        Me.txtID.Name = "txtID"
        Me.txtID.Size = New System.Drawing.Size(232, 20)
        Me.txtID.TabIndex = 12
        '
        'lblID
        '
        Me.lblID.BackColor = System.Drawing.Color.Gray
        Me.lblID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.lblID.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblID.ForeColor = System.Drawing.Color.White
        Me.lblID.Location = New System.Drawing.Point(11, 12)
        Me.lblID.Name = "lblID"
        Me.lblID.Size = New System.Drawing.Size(124, 20)
        Me.lblID.TabIndex = 9
        Me.lblID.Text = "ID:"
        Me.lblID.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
        '
        'btnSave
        '
        Me.btnSave.Location = New System.Drawing.Point(246, 204)
        Me.btnSave.Name = "btnSave"
        Me.btnSave.Size = New System.Drawing.Size(127, 38)
        Me.btnSave.TabIndex = 16
        Me.btnSave.Tag = "row.Value(indexAnalyte)"
        Me.btnSave.Text = "&Save"
        Me.btnSave.UseVisualStyleBackColor = True
        '
        'cboDate
        '
        Me.cboDate.BackColor = System.Drawing.SystemColors.Window
        Me.cboDate.ForeColor = System.Drawing.Color.Black
        Me.cboDate.FormattingEnabled = True
        Me.cboDate.Location = New System.Drawing.Point(141, 166)
        Me.cboDate.Name = "cboDate"
        Me.cboDate.Size = New System.Drawing.Size(232, 21)
        Me.cboDate.TabIndex = 20
        '
        'cboBurnItem2
        '
        Me.cboBurnItem2.BackColor = System.Drawing.SystemColors.Window
        Me.cboBurnItem2.ForeColor = System.Drawing.Color.Black
        Me.cboBurnItem2.FormattingEnabled = True
        Me.cboBurnItem2.Location = New System.Drawing.Point(141, 134)
        Me.cboBurnItem2.Name = "cboBurnItem2"
        Me.cboBurnItem2.Size = New System.Drawing.Size(232, 21)
        Me.cboBurnItem2.TabIndex = 19
        '
        'lblDate
        '
        Me.lblDate.BackColor = System.Drawing.Color.Gray
        Me.lblDate.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.lblDate.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblDate.ForeColor = System.Drawing.Color.White
        Me.lblDate.Location = New System.Drawing.Point(11, 166)
        Me.lblDate.Name = "lblDate"
        Me.lblDate.Size = New System.Drawing.Size(124, 20)
        Me.lblDate.TabIndex = 17
        Me.lblDate.Text = "Link Field:"
        Me.lblDate.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
        '
        'lblBurnItem2
        '
        Me.lblBurnItem2.BackColor = System.Drawing.Color.Gray
        Me.lblBurnItem2.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.lblBurnItem2.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblBurnItem2.ForeColor = System.Drawing.Color.White
        Me.lblBurnItem2.Location = New System.Drawing.Point(11, 135)
        Me.lblBurnItem2.Name = "lblBurnItem2"
        Me.lblBurnItem2.Size = New System.Drawing.Size(124, 20)
        Me.lblBurnItem2.TabIndex = 18
        Me.lblBurnItem2.Text = "Burn Item2:"
        Me.lblBurnItem2.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
        '
        'frmBurnlines
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(388, 254)
        Me.Controls.Add(Me.cboDate)
        Me.Controls.Add(Me.cboBurnItem2)
        Me.Controls.Add(Me.lblDate)
        Me.Controls.Add(Me.lblBurnItem2)
        Me.Controls.Add(Me.txtBurnItem)
        Me.Controls.Add(Me.txtLength)
        Me.Controls.Add(Me.txtName)
        Me.Controls.Add(Me.lblBurnItem)
        Me.Controls.Add(Me.lblLength)
        Me.Controls.Add(Me.lblName)
        Me.Controls.Add(Me.txtID)
        Me.Controls.Add(Me.lblID)
        Me.Controls.Add(Me.btnSave)
        Me.MaximizeBox = False
        Me.Name = "frmBurnlines"
        Me.Text = "Burnlines"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents txtBurnItem As System.Windows.Forms.TextBox
    Friend WithEvents txtLength As System.Windows.Forms.TextBox
    Friend WithEvents txtName As System.Windows.Forms.TextBox
    Friend WithEvents lblBurnItem As System.Windows.Forms.Label
    Friend WithEvents lblLength As System.Windows.Forms.Label
    Friend WithEvents lblName As System.Windows.Forms.Label
    Friend WithEvents txtID As System.Windows.Forms.TextBox
    Friend WithEvents lblID As System.Windows.Forms.Label
    Friend WithEvents btnSave As System.Windows.Forms.Button
    Friend WithEvents cboDate As System.Windows.Forms.ComboBox
    Friend WithEvents cboBurnItem2 As System.Windows.Forms.ComboBox
    Friend WithEvents lblDate As System.Windows.Forms.Label
    Friend WithEvents lblBurnItem2 As System.Windows.Forms.Label
End Class
