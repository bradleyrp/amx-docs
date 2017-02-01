#!/bin/bash

<<notes
Bootstrap script for (current) semi-public implementation of ACME/AUTOMACS
notes

dest=$1
server="green"
up="http://github.com/bradleyrp/"
up_private="/home/localshare/master/CODES/"

if [ -z "$dest" ]; then echo "[USAGE] ./scriptname <new_folder>" && exit 1; fi
if [ -d "$dest" ]; then echo "[ERROR] $dest exists" && exit 1; fi
if [[ $HOSTNAME =~ $server ]]; then server=""; else server=$server":"; fi

#---clone acme 
git clone $up/acme $dest

#---use a default config.py
cat <<EOF > $dest/config.py
#!/usr/bin/env python -B
{'commands':['./acme.py'],
 'inputs': '@regex^.*?_expts\\.py$',
 'cleanup':['exec.py','s*-*','state*.json','expt*.json','script*.py','log-*','*.log','v*-*'],
 'commands_aliases': [('prep?', 'preplist'), ('set', 'set_config')]}
EOF
cd $dest

#---set up the environment (use kwargs and quotes for http sources)
make set module source="$up/acme.amx" spot="amx"
make set commands amx/cli.py
make set module source="$up/acme.amx.docs" spot="inputs/docs"
make set commands inputs/docs/docs.py
make set module source="$up/acme.amx.extras" spot="inputs/extras"
make set module source="$up/acme.amx.proteins" spot="inputs/proteins"
make set module source="$up/acme.amx.bilayers" spot="inputs/bilayers"
make set module source="$up/acme.amx.vmd" spot="vmd"
make set module source="$server$up_private/acme.amx.proteins.structures.git" spot="inputs/proteins/structures"
make set module source="$server$up_private/acme.amx.martini.git" spot="inputs/martini"
