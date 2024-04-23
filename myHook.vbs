Set args = WScript.Arguments
'Dim flag, python, main
flag = 0
'python = "D:\developerTools\Python310\python.exe"
main = "main.py"
For Each arg In args
	If arg="-debug" Then
		flag=1
		Exit For
	End If
Next
Set ws = CreateObject("Wscript.Shell")

If flag=0 Then
	ws.run "python" & " " & main, 0
Else
	ws.run "python" & " " & main, 1
End If
