.PHONY: test profile

profile:
	python -m cProfile -o profile after.py 
	python topten.py

test:
	cd test; python all_test.py
	python vector.py

clean:
	rm -f *~ *.pyc
