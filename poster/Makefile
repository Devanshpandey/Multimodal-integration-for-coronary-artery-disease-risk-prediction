.PHONY: all build qa clean
all: build qa
build:
	python3 build_poster.py
qa:
	python3 qa_checks.py
clean:
	rm -f output/*.pdf output/*.png qa/*.png qa/qa_report.json
