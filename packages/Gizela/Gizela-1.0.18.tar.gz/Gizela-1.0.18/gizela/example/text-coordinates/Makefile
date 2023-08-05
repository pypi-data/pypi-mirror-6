proj=$(wildcard epoch*.txt)
coord2gamaObs=coord2gamaObs.py
gizela=gama-data-adj.py
# id testovanych bodu
#id_test=117,118
gizela_opt= --local-system-2d \
            --config=default.cfg \
            --config-fig=default-fig.cfg \
            --fig-scale=1:5000 \
            --displ-scale-xy=10000:1 \
            --title="Title" \
            --subtitle="Subtitle"\
            --plot-xy \
            --use-apriori \

all:
	make $(proj:.txt=.gkf)
	make $(proj:.txt=.xml)
	# vykresleni strednich elips chyb
	#$(gizela) $(gizela_opt) --conf-prob=0.39 --test-id=$(id_test) --show-figure --save-xy=posuny-elipsy.png $(proj:.txt=.xml)
	$(gizela) $(gizela_opt) --conf-prob=0.39 --show-figure --save-xy=posuny-elipsy.png --print-displacements=displacements.txt $(proj:.txt=.xml)
	$(gizela) $(gizela_opt) --conf-prob=0.39 --print-coordinates=coordinates.txt $(proj:.txt=.xml)

	# testovani
	$(gizela) $(gizela_opt) --conf-prob=0.98 --test-xy --print-test=testy-posunu.txt --show-figure --save-xy=posuny-test.png $(proj:.txt=.xml)

epoch0.gkf: epoch0.txt
	$(coord2gamaObs) --sigma-xy=0.001 $< >$@
	
%.gkf: %.txt
	$(coord2gamaObs) $< >$@


%.xml: %.gkf
	gama-local --text $(<:.gkf=.adj) --xml $@ $<

clean:
	rm -f $(proj:.txt=.gkf)
	rm -f $(proj:.txt=.adj)
	rm -f $(proj:.txt=.xml)
	rm -f posuny-elipsy.png posuny-test.png testy.txt obrazek-test.png coordinates.txt displacements.txt testy-posunu.txt
