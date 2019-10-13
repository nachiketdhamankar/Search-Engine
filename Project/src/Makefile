clean:
	rm -r __pycache__

parse:
	python parser.py -case

index:
	python indexer.py
	python indexer.py -stop
	python indexer.py -stem

jm:
	python jmsmoothing.py
	python jmsmoothing.py -stem
	python jmsmoothing.py -stop

tfidf:
	python tfidf.py
	python tfidf.py -stem
	python tfidf.py -stop

bm25:
	python bm25.py
	python bm25.py -stem
	python bm25.py -stop

lucene:
	javac -cp lib/*:. lucene.java
	java -cp lib/*:. lucene

	# /Users/samkeet/Downloads/IR-Project/data/model/regular
	# /Users/samkeet/Downloads/IR-Project/data/corpus

	# /Users/samkeet/Downloads/IR-Project/data/model/stem
	# /Users/samkeet/Downloads/IR-Project/data/stem_corpus

snippet:
	python snippetgenerator.py -d -m bm25 -f stem_False_stop_False_bm25_score.json

eval:
	python evaluation.py