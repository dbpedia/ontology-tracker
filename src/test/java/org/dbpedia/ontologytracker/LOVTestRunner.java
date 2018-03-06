package org.dbpedia.ontologytracker;

import org.apache.jena.rdf.model.Model;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.util.*;

import javax.net.ssl.HttpsURLConnection;

public class LOVTestRunner {

    public static final String repositoryAddress = "http://lov.okfn.org/dataset/lov/api/v2/vocabulary/list";

    public static final ArrayList<String> ontologiesURLs = new ArrayList<String>();

    public static Logger logger = LoggerFactory.getLogger(LOVTestRunner.class);

    public static void main(String[] args) {
        logger.info("Checking the LOV cloud...");
        parse();
        logger.info("Starting tests...");
        streamAndRunTests(ontologiesURLs);
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

        } catch (IOException e) {
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
    public static InputStream getStream(String downloadURL) throws IOException {
        BufferedInputStream out = null;
        HttpURLConnection httpConn;
        httpConn = (HttpURLConnection) new URL(downloadURL).openConnection();
        httpConn.setRequestMethod("GET");
        httpConn.setReadTimeout(2000);
        httpConn.setConnectTimeout(2000); //read and connection timeout at 20s
        httpConn.setRequestProperty("Content-type", "application/rdf+xml");
        httpConn.setRequestProperty("Accept", "application/rdf+xml");

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
                    httpsConn.setRequestProperty("Accept", "application/rdf+xml");
                    hdrs = httpsConn.getHeaderFields();
                    hdrKeys = hdrs.keySet();
                    for (String k : hdrKeys) {
                        System.out.println("Key: " + k + "  Value: " + hdrs.get(k));

                    }
                    try {
                        out = new BufferedInputStream(httpsConn.getInputStream());
                    } catch (Exception e) {
                        e.printStackTrace();
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
                    httpsConn.setRequestProperty("Accept", "application/rdf+xml");
                    hdrs = httpsConn.getHeaderFields();
                    hdrKeys = hdrs.keySet();
                    for (String k : hdrKeys) {
                        System.out.println("Key: " + k + "  Value: " + hdrs.get(k));

                    }
                    try {
                        out = new BufferedInputStream(httpsConn.getInputStream());
                    } catch (SocketTimeoutException e) {
                        e.printStackTrace();
                    }
                    return out;
                }
            }
        }
        try {
            out = new BufferedInputStream(httpConn.getInputStream());
        } catch (SocketTimeoutException e) {
            e.printStackTrace();
        }

        return out;
    }


    /**
     * Stream ontologies from URLs and run tests against them
     *
     * @param urls an ArrayList<string> containing URLs to be read
     */
    public static void streamAndRunTests(ArrayList<String> urls) {

        for (String url : urls) {

            Model model = null;

            //@TODO include the SHACL tests here
            String test = "";

            String result;

            logger.info("Streaming " + url);

            try (InputStream ontology = getStream(url);) {
                if (ontology != null) {
                    logger.info(url + " successfully read");

                    try {
                        model = ValidateOntology.readOntology(ontology, "RDF/XML");
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    if (model.size() == 0) {
                        logger.error(url + " has " + model.size() + " elements. Skipping it...");
                        continue;
                    }
                    logger.info(url + " has " + model.size() + " elements");
                    logger.info("Running tests on " + url);

                    result = ValidateOntology.runShaclTests(model, test);


                    logger.info("Test results: " + result);
                } else logger.error(url + " could not be read. Skipping it...");
            } catch (Exception e) {
                e.printStackTrace();
            }

        }

    }

}