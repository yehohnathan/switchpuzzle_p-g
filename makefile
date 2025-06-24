PY   ?= py -3.12
MAIN := switchpuzzle.py

install:
	$(PY) -m pip install --upgrade ruff pyinstaller

run: install
	$(PY) $(MAIN)

lint:
	$(PY) -m pip install --upgrade ruff
	ruff check --fix $(MAIN)

exe: install
	pyinstaller --onefile --windowed $(MAIN)

.PHONY: install run lint exe
