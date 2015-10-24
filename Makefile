.PHONY: test profile

profile:
	python -m cProfile -o profile after.py 
	python topten.py

test:
	cd test; python all_test.py
	python vector.py

clean:
	find . -name '*~' -exec rm -f {} \;
	find . -name '*.py[co]' -exec rm -f {} \;
