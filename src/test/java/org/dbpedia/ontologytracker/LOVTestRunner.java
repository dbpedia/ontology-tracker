package org.dbpedia.ontologytracker;

import org.apache.jena.rdf.model.Model;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;

import javax.net.ssl.HttpsURLConnection;

public class LOVTestRunner {

    public static final String repositoryAddress = "http://lov.okfn.org/dataset/lov/api/v2/vocabulary/list";

    public static final ArrayList<String> ontologiesURLs = new ArrayList<String>();

    public static Logger logger = LoggerFactory.getLogger(LOVTestRunner.class);

    public static int success = 0;

    public static int fail = 0;

    public static int tested = 0;

    public static final String FORMATS = "application/rdf+xml, text/turtle";
    
    private static String outdir = "/home/gpublio/ontology-tracker/lovresults";

    public static void main(String[] args) throws IOException
    {
        new File(outdir).mkdirs();
        logger.info("Checking the LOV cloud...");
        parse();
        logger.info("Starting tests...");
        streamAndRunTests(ontologiesURLs);
        logger.info("Ontologies not tested: " + fail);
        logger.info("Ontologies tested: " + success);
    }

    /**
     * Parses the JSON file
     */
    public static void parse() {
        try {
            JSONTokener tokener = new JSONTokener(new URL(repositoryAddress).openStream());
            JSONArray root = new JSONArray(tokener);

            Iterator<Object> it = root.iterator();
            while (it.hasNext()) {
                ontologiesURLs.add(((JSONObject) it.next()).get("uri").toString());
            }
            logger.info("Found " + ontologiesURLs.size() + " ontologies URLs.");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Open a connection and return the stream
     *
     * @param downloadURL the URL to download the file
     *
     * @return
     * @throws IOException
     */
    public static InputStream getStream(String downloadURL) throws Exception {

        BufferedInputStream out = null;
            HttpURLConnection httpConn;
            httpConn = (HttpURLConnection) new URL(downloadURL).openConnection();
            httpConn.setRequestMethod("GET");
            httpConn.setReadTimeout(2000);
            httpConn.setConnectTimeout(2000); //read and connection timeout at 20s
            httpConn.setRequestProperty("Content-type", "application/rdf+xml");
            httpConn.setRequestProperty("Accept", FORMATS);

            Map<String, List<String>> hdrs = httpConn.getHeaderFields();
            Set<String> hdrKeys = hdrs.keySet();

            CharSequence moved1 = "HTTP/1.1 301"; //moved permanently
            CharSequence moved2 = "HTTP/1.1 302"; //moved temporarily
            CharSequence seeOther = "HTTP/1.1 303"; //see other
            CharSequence secureHttp = "https://";
            for (String k : hdrKeys) {
                System.out.println("Key: " + k + "  Value: " + hdrs.get(k));

            }

            if (hdrKeys.contains(null)) {
                if (hdrs.get(null).toString().contains(moved1) || hdrs.get(null).toString().contains(moved2)) { //this means redirect; trying new URL
                    if (hdrs.get("Location").toString().contains(secureHttp)) {
                        httpConn.disconnect();
                        HttpsURLConnection httpsConn;
                        httpsConn = (HttpsURLConnection) new URL(hdrs.get("Location").toString().replace("[", "").replace("]", "")).openConnection();
                        httpsConn.setRequestMethod("GET");
                        httpsConn.setReadTimeout(2000);
                        httpsConn.setConnectTimeout(2000); //read and connection timeout at 20s
                        httpsConn.setRequestProperty("Content-type", "application/rdf+xml");
                        httpsConn.setRequestProperty("Accept", "application/rdf+xml, text/turtle");
                        hdrs = httpsConn.getHeaderFields();
                        hdrKeys = hdrs.keySet();
                        for (String k : hdrKeys) {
                            System.out.println("Key: " + k + "  Value: " + hdrs.get(k));

                        }
                        try {
                            out = new BufferedInputStream(httpsConn.getInputStream());
                        } catch (Exception e) {
                            throw e;
                        }
                        return out;
                    } else if (hdrKeys.contains(null) && hdrs.get(null).toString().contains(seeOther)) {
                        httpConn.disconnect();
                        HttpsURLConnection httpsConn;
                        httpsConn = (HttpsURLConnection) new URL(downloadURL.replace("http", "https")).openConnection();
                        httpsConn.setRequestMethod("GET");
                        httpsConn.setReadTimeout(2000);
                        httpsConn.setConnectTimeout(2000); //read and connection timeout at 20s
                        httpsConn.setRequestProperty("Content-type", "application/rdf+xml");
                        httpsConn.setRequestProperty("Accept", FORMATS);
                        hdrs = httpsConn.getHeaderFields();
                        hdrKeys = hdrs.keySet();
                        for (String k : hdrKeys) {
                            System.out.println("Key: " + k + "  Value: " + hdrs.get(k));

                        }
                        try {
                            out = new BufferedInputStream(httpsConn.getInputStream());
                        } catch (Exception e) {
                            throw e;
                        }
                        return out;
                    }
                }
            }
            try {
                out = new BufferedInputStream(httpConn.getInputStream());
            } catch (Exception e) {
                throw e;
            }


        return out;
    }


    /**
     * Stream ontologies from URLs and run tests against them
     *
     * @param urls an ArrayList<string> containing URLs to be read
     */
    public static void streamAndRunTests(ArrayList<String> urls) throws IOException {

        FileWriter fw = new FileWriter(outdir + File.separator + "results_daniel.csv");

        String fwOutput = "ontology;size;test;fail\n";
        String test = "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n" +
                "@prefix sh: <http://www.w3.org/ns/shacl#> .\n" +
                "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" +
                "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n" +
                "@prefix gdl-shape: <http://dbpedia.org/gdl-shape#> .\n" +
                "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n" +
                "gdl-shape:\n" +
                "rdfs:label \"SHACL for Ontology Guidelines\"@en ;\n" +
                "rdfs:comment \"This graph is used to validate ontologies against pre-selected tests. \"@en ;\n" +
                "sh:declare [\n" +
                "sh:prefix \"rdfs\" ;\n" +
                "sh:namespace \"http://www.w3.org/2000/01/rdf-schema#\"^^xsd:anyURI ;\n" +
                "] ;\n" +
                "sh:declare [\n" +
                "sh:prefix \"owl\" ;\n" +
                "sh:namespace \"http://www.w3.org/2002/07/owl#\"^^xsd:anyURI ;\n" +
                "] ;\n" +
                "sh:declare [\n" +
                "sh:prefix \"rdf\" ;\n" +
                "sh:namespace \"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"^^xsd:anyURI ;\n" +
                "] ;\n" +
                "sh:declare [\n" +
                "sh:prefix \"gdl\" ;\n" +
                "sh:namespace \"http://dbpedia.org/ontology-guidelines/\"^^xsd:anyURI ;\n" +
                "] .\n" +
                "\n" +
                "gdl-shape:ClassShape\n" +
                "a sh:Shape;\n" +
                "sh:targetClass owl:Class;\n" +
                "sh:targetSubjectsOf rdfs:subClassOf;\n" +
                "sh:property [\n" +
                "sh:message \"Classes must have a label\";\n" +
                "sh:path rdfs:label;\n" +
                "sh:minCount 1;\n" +
                "sh:dataType rdf:langString;\n" +
                "sh:uniqueLang true; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Classes must have a comment\";\n" +
                "sh:path rdfs:comment;\n" +
                "sh:minCount 1;\n" +
                "sh:dataType rdf:langString;\n" +
                "sh:uniqueLang true; ];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Classes must have at most one superclass\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT DISTINCT $this\n" +
                "WHERE {\n" +
                "  $this rdf:type owl:Class .\n" +
                "  $this rdfs:subClassOf ?v1 .\n" +
                "  $this rdfs:subClassOf ?v2 .\n" +
                "  FILTER NOT EXISTS {?v1 rdfs:subClassOf ?v2 }.\n" +
                "  FILTER NOT EXISTS {?v2 rdfs:subClassOf ?v1 }.\n" +
                "  FILTER(?v1 != ?v2) .\n" +
                "  FILTER(?v1 != owl:Thing) .\n" +
                "  FILTER(?v2 != owl:Thing) .\n" +
                "  FILTER($this != ?v1) .\n" +
                "  FILTER($this != ?v2) .\n" +
                "}\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Classes names must not start with a lowercase letter\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this \n" +
                "WHERE { \n" +
                "  $this a owl:Class .\n" +
                "  BIND(REPLACE(STR($this), '/([a-z][1]?[A-z0-9]*)$', '' ) as ?str1) .\n" +
                "  FILTER(STR($this) != STR(?str1)) .\n" +
                "}\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Classes must have instances\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT DISTINCT ?value $this \n" +
                "WHERE { \n" +
                "  $this a owl:Class .\n" +
                "  OPTIONAL { ?value a $this } .\n" +
                "}\n" +
                "GROUP BY $this ?value\n" +
                "HAVING (COUNT(?value) = 0 )\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Detect synonyms created as classes\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this \n" +
                "WHERE { \n" +
                "  $this a owl:Class .\n" +
                "  $this owl:equivalentClass ?other\n" +
                "  BIND(REPLACE(STR($this), '(#|/)[^#/]*$', '$1' ) as ?ns1) .\n" +
                "  BIND(REPLACE(STR(?other), '(#|/)[^#/]*$', '$1' ) as ?ns2) .\n" +
                "  FILTER(?ns1 = ?ns2) .\n" +
                "}\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Detect unconnected classes\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this WHERE\n" +
                "{\n" +
                "  $this a owl:Class .\n" +
                "  FILTER NOT EXISTS {$this rdfs:subClassOf ?any1} .\n" +
                "  FILTER NOT EXISTS {?any2 owl:equivalentClass $this} .\n" +
                "  FILTER NOT EXISTS {$this owl:equivalentClass ?any3} .\n" +
                "  FILTER NOT EXISTS {?any4 rdfs:subClassOf $this} .\n" +
                "  FILTER NOT EXISTS {?any5 rdfs:range $this} .\n" +
                "  FILTER NOT EXISTS {?any6 rdfs:domain $this} .\n" +
                "}\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Detect cycles in the class hierarchy\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this WHERE\n" +
                "{\n" +
                "  $this a owl:Class .\n" +
                "  $this rdfs:subClassOf+ $this .\n" +
                "}\n" +
                "\"\"\";\n" +
                "] .\n" +
                "\n" +
                "\n" +
                "\n" +
                "gdl-shape:PropertyShape\n" +
                "a sh:Shape;\n" +
                "sh:targetClass rdf:Property;\n" +
                "sh:targetClass owl:DatatypeProperty;\n" +
                "sh:targetClass owl:ObjectProperty;\n" +
                "sh:targetSubjectsOf rdfs:subPropertyOf;\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have a label\";\n" +
                "sh:path rdfs:label;\n" +
                "sh:minCount 1;\n" +
                "sh:dataType rdf:langString;\n" +
                "sh:uniqueLang true; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have a comment\";\n" +
                "sh:path rdfs:comment;\n" +
                "sh:minCount 1;\n" +
                "sh:dataType rdf:langString;\n" +
                "sh:uniqueLang true; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have at most one domain\";\n" +
                "sh:path rdfs:domain;\n" +
                "sh:maxCount 1; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have at least one domain, which is a class\";\n" +
                "sh:path rdfs:domain;\n" +
                "sh:minCount 1;\n" +
                "sh:class owl:Class; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have at most one range\";\n" +
                "sh:path rdfs:range;\n" +
                "sh:maxCount 1; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have at least one range, which is a class\";\n" +
                "sh:path rdfs:range;\n" +
                "sh:minCount 1;\n" +
                "sh:class owl:Class; ];\n" +
                "\n" +
                "sh:property [\n" +
                "sh:message \"Properties must have at most one superproperty\";\n" +
                "sh:path rdfs:subPropertyOf;\n" +
                "sh:maxCount 1; ];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Properties names must not start with a capital letter\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this \n" +
                "WHERE { \n" +
                "  $this a ?property .\n" +
                "  FILTER(?property IN (rdf:Property, owl:DatatypeProperty, owl:ObjectProperty)) .\n" +
                "  BIND(REPLACE(STR($this), '/[A-Z][A-z0-9]*$', '' ) as ?str1) .\n" +
                "  FILTER(STR($this) != STR(?str1)) .\n" +
                "}\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Detect relationships inverse to themselves\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this \n" +
                "WHERE { \n" +
                "  $this a ?property .\n" +
                "  $this owl:inverseOf $this .\n" +
                "  FILTER(?property IN (rdf:Property, owl:DatatypeProperty, owl:ObjectProperty)) .\n" +
                "}\n" +
                "\"\"\";\n" +
                "];\n" +
                "\n" +
                "sh:sparql [\n" +
                "sh:message \"Detect wrongly defined relationship 'is'\";\n" +
                "sh:select \"\"\"\n" +
                "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" +
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" +
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" +
                "SELECT $this \n" +
                "WHERE { \n" +
                "  $this a owl:ObjectProperty .\n" +
                "  BIND(REPLACE(STR($this), 'isA', '' ) as ?str1) .\n" +
                "  BIND(REPLACE(STR($this), 'is-a', '' ,'i') as ?str2) .\n" +
                "  BIND(REPLACE(STR($this), 'is_a', '' ,'i') as ?str3) .\n" +
                "  FILTER(STR($this) != STR(?str1) || STR($this) != STR(?str2) || STR($this) != STR(?str3)) .\n" +
                "}\n" +
                "\"\"\";\n" +
                "] .";

        String result;

        List<DBpediaTestResult> testResults;

        //ArrayList<List<DBpediaTestResult>> allTests = new ArrayList<>(300);
        ArrayList<String> allTests = new ArrayList<>(450);

        for (String url : urls) {

            tested = tested+1;

            Model model = null;

            logger.info("Streaming " + url);

            /*try (InputStream ontology = getStream(url)) {
                if (ontology != null) {
                    logger.info(url + " successfully read");
                    if(url.equals("http://ns.inria.fr/emoca") || url.equals("http://purl.org/limo-ontology/limo/") || url.equals("http://linkedscience.org/lsc/ns#") || url.equals("https://talespaiva.github.io/step/")) {
                        fail = fail + 1;
                        continue; //skip broken ontologies
                    }
                    try {
                        model = ValidateOntology.readOntology(ontology, "RDF/XML");
                    } catch (Exception e) {
                        fail = fail + 1;
                        throw e;
                    }
                    if (model.size() == 0) {
                        logger.error(url + " has " + model.size() + " elements. Skipping it...");
                        fail = fail + 1;
                        continue;
                    }
                    logger.info(url + " has " + model.size() + " elements");
                    logger.info("Running tests on " + url);


                    testResults = ValidateOntology.returnShaclTests(model, test);
                    //result = ValidateOntology.runTests(model, "RDFXML", test);

                    Map<String, Integer> testMap = new HashMap<String, Integer>();

                    for(DBpediaTestResult thisResult : testResults) {
                        if(testMap.containsKey(thisResult.message)) {
                            int oldValue = testMap.get(thisResult.message);
                            testMap.put(thisResult.message, oldValue+1);
                        }
                        else testMap.put(thisResult.message, 1);
                    }
                    for (Map.Entry<String, Integer> entry : testMap.entrySet())
                    {
                        fwOutput += url +";"+model.size()+";"+entry.getKey()+";" + entry.getValue()+"\n";
                    }


                    //logger.info("Test results: " + testResults.size() + " occurrences");
                    success = success + 1;


                    //allTests.add(testResults);
                } else
                {
                    logger.error(url + " could not be read. Skipping it...");
                    fail = fail + 1;
                }
            } catch (Exception e) {
                e.printStackTrace();
                fail = fail+1;
            }*/

        }

        fw.write(fwOutput);
        fw.close();

        logger.info("tested: " + tested);
        logger.info("success: " + success);
        logger.info("failed: "+ fail);
    }

}