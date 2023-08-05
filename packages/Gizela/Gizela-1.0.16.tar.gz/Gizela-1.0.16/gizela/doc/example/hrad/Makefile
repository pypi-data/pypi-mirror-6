bin=/home/kubin/git/gizela/bin
path=/home/kubin/git/gizela

# id testovanych bodu
#id_test_vrt=1001,1002,1003,1005,1011,1012
id_test_vrt=1001,1002,1003,1005,1012
id_test_gps=501,513,524,541,508,508N
id_test_pol=502,504,505,506,507,509,510,511,512,525,526,527,532,552,553
id_test=$(id_test_pol),$(id_test_gps),$(id_test_vrt)

gizela_adj=$(bin)/gama-data-adj.py \
		  --local-system-2d \
		  --config=hrad.cfg \
	      --config-fig=hrad-fig.cfg \
	      --fig-scale=1:4200 \
	      --displ-scale-xy=4200:2 \
	      --title="Title" \
	      --subtitle="Subtitle"\
		  --plot-xy \
		  --use-apriori \

#gama=gama-local --cov-band 1
gama=gama-local 
		  

vypocet:
	# vyrovnani GNU Gama
	$(gama) --xml hrad0806.adj hrad0806.gkf
	$(gama) --xml hrad0811.adj hrad0811.gkf
	$(gama) --xml hrad1004.adj hrad1004.gkf
	$(gama) --xml hrad1010.adj hrad1010.gkf

	# local copy
	export PYTHONPATH=$(path)
	echo $(PYTHONPATH)

    # vykresleni site a elips
	$(gizela_adj) --conf-prob=0.39 --test-id=$(id_test_vrt) --show-figure --save-xy=obrazek-elipsy.png hrad0806.adj hrad0811.adj hrad1004.adj hrad1010.adj

	# testovani
	#$(gizela_adj) --test-xy --print-test=testy.txt --show-figure --save-xy=obrazek-test.png hrad0806.adj hrad0811.adj hrad1004.adj hrad1010.adj
	$(gizela_adj) --conf-prob=0.98 --test-xy --print-test=testy.txt --test-id=$(id_test_vrt) --show-figure --save-xy=obrazek-test.png hrad0806.adj hrad0811.adj hrad1004.adj hrad1010.adj

clean:
	rm -f *.adj
	rm -f obrazek-elipsy.png testy.txt obrazek-test.png
