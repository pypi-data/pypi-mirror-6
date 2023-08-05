cfg=epydoc.cfg
cfg_local= epydoc-local.cfg

all:
	epydoc --config $(cfg)

check:
	epydoc --check --config $(cfg)

verb:
	epydoc -v --config $(cfg)

sync:
	make all
	rsync -av html/ slon:/var/www/gizela/html

local:
	epydoc --config $(cfg_local)
