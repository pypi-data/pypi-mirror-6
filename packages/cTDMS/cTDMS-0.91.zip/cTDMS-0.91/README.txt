Was muss ich machen um ein Update des cTDMS Packetes zu erzeugen

1. unter .. sphinx die rst files editieren
	dann mit :
	make html 
	die html dateien in sphinx/_build erzeugen
	
2. den Ordner sphinx/_build/html
nach PyTDMSentwicklung/cTDMS kopieren

alle sourcefiles wie cTDMS.py oder setup.py nach PyTDMSentwicklung/cTDMS kopieren

3. unter PyTDMSentwicklung eine cmd shell öffnen
und die Distribution erzeugen

cmd_shell öffnen.
python setup.py bdist
python setup.py bdist_wininst
python setup.py sdist

