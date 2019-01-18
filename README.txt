The results of the projects are saved in their respective 'Phase' and 'Extra Credits' folders
(If you wish to see Evaluation, kindly open the 'Phase 3' folder and so on)

All .csv and .json output files are stored in 'Phase' folders 

Run Instructions:

Project Structure:
./data
    ./cacm
    ./corpus
    ./index
    ./model
    ./stem_corpus
    cacm_stem.txt
    cacm.query.txt
    cacm.rel.txt
    cacm_stem.query.txt
    common_words
./lib
    .. (lucene jars) ..
./results
    ./bm25
    ./bm25_stop
    ./bm25_enrich
    ./jm
    ./jm_stop
    ./tfidf
    ./tfidf_stop
    ./lucene
    .. (outputs of running models and evaluation) ..
./src
    .. (all program source code here) .. 

===============================================================================

Follwing commands are to be run from the src directory

[0] Preprocessing: this step involves pre-processing the cacm.queries.txt, cacm.rel.txt
    python parser_cacm_query.py
    python parser_query_map.py
    python parser_cacm_rel.py

[1] Parsing and cleaning corpus
    python parser.py -case

[2] Parsing stem corpus
    python parser_cacm_stem_corpus.py

[3] Create 3 Inverted indexes
    python indexer.py
    python indexer.py -stop
    python indexer.py -stem

[4] JM Smoothing
    python jmsmoothing.py
    python jmsmoothing.py -stem
    python jmsmoothing.py -stop

[5] TF-IDF
    python tfidf.py
    python tfidf.py -stem
    python tfidf.py -stop

[6] BM25
    python bm25.py
    python bm25.py -stem
    python bm25.py -stop

[7] Lucene
    javac -cp lib/*:. lucene.java
    java -cp lib/*:. lucene

To parse the results from the files
    python parser_lucene_result.py

[8] Query Enrichment Run
    python query_enrichment.py

[9] Snippet Generation
    python snippetgenerator.py -d -m bm25 -f stem_False_stop_False_bm25_score.json

[10] Evaluation
    python evaluation.py

[11] Extra Credit
    -q is the query to search
    -e is given for exact match search
    -n is used for proxity search and accepts and integer value

    python advanced_search.py -b -q "computers ibm" > best_match.txt
    python advanced_search.py -e -q "operating system" > exact_match.txt
    python advanced_search.py -n 3 -q "parallel methods" > proximity_match.txt


=============================================================================
Requirements & Libraries
Python3.7.1
Pandas0.23
BeautifulSoup4.6.3
Matplotlib3.0.2

Lucene:
    lucene-analyzers-common-4.7.2.jar
    lucene-core-4.7.2.jar
    lucene-queryparser-4.7.2.jar