foreach($p in $(pip freeze)){ pip install -U $p.Split("=")[0]}
