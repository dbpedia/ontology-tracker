package org.dbpedia.ontologytracker;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.GeneralSecurityException;
import java.security.cert.X509Certificate;
import java.util.*;

import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

public class LOVCloudDownloader {

    public static final String repositoryAddress = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list";

    public static String checkPrefixAddress = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info?vocab=";

    public static String nsp;
    public static String prefix;

    public static final HashMap<String, String> prefixesAndNsps = new HashMap<>();

    public static Logger logger = LoggerFactory.getLogger(LOVTestRunner.class);
    
    public static int downloaded = 0;

    public static final String FORMATS = "application/rdf+xml, text/turtle";

    private static String outdir = "/home/gpublio/ontology-tracker/ontologies";

    public static void main(String[] args) throws IOException
    {
        new File(outdir).mkdirs();
        logger.info("Checking the LOV cloud...");
        parse();
        logger.info("Beginning download process...");
        streamAndSave(prefixesAndNsps);
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
                JSONObject obj = ((JSONObject) it.next());
                prefixesAndNsps.put(obj.get("prefix").toString(), obj.get("nsp").toString());
            }
            logger.info("Found " + prefixesAndNsps.size() + " ontologies on list.");

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
    public static InputStream getStream(String downloadURL) throws IOException {

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
        CharSequence forbidden = "HTTP/1.1 403"; //forbidden; see other
        CharSequence secureHttp = "https://";
        for (String k : hdrKeys) {
            System.out.println("Key: " + k + "  Value: " + hdrs.get(k));

        }


        // Create a trust manager that does not validate certificate chains
        TrustManager[] trustAllCerts = new TrustManager[] {
                new X509TrustManager() {
                    public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                        return new X509Certificate[0];
                    }
                    public void checkClientTrusted(
                            java.security.cert.X509Certificate[] certs, String authType) {
                    }
                    public void checkServerTrusted(
                            java.security.cert.X509Certificate[] certs, String authType) {
                    }
                }
        };

        // Install the all-trusting trust manager
        try {
            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());
            HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
        } catch (GeneralSecurityException e) {
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
                } else if (hdrKeys.contains(null) && hdrs.get(null).toString().contains(seeOther) || hdrs.get(null).toString().contains(forbidden) ) {
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

    public static void streamAndSave(HashMap<String, String> prefixes) throws IOException {


        String result;

        //List<DBpediaTestResult> testResults;

        //ArrayList<List<DBpediaTestResult>> allTests = new ArrayList<>(300);
        //ArrayList<String> allTests = new ArrayList<>(450);

        for (String prefix : prefixes.keySet()) {

            downloaded = downloaded+1;

            String nsp = prefixes.get(prefix);

            //logger.info("Saving " + prefix + " in namespace dir " + nsp);

            logger.info("Checking all versions of prefix " + prefix);

            HashMap<String, String> namesAndURLs = new HashMap<>();
            JSONTokener tokener = new JSONTokener(new URL(checkPrefixAddress+prefix).openStream());
            JSONArray root;
            try{
                root = new JSONObject(tokener).getJSONArray("versions");
            }
            catch (JSONException e) {
                continue;
            }

            for (Object o : root) {
                if ( o instanceof JSONObject ) {
                    try {
                        namesAndURLs.put(((JSONObject) o).get("name").toString(), ((JSONObject) o).get("fileURL").toString());
                    }
                    catch(Exception e) {}
                }
            }
            //Iterator<Object> it = root.toJSONArray(root.names()).iterator();
            //while (it.hasNext()) {
            //    namesAndURLs.put(((JSONObject) it.next()).get("name").toString(), ((JSONObject) it.next()).get("fileURL").toString());
            //}

            String pattern = "(https?|ftp):\\/\\/([^/\\r\\n]+)(\\/[^\\r\\n]*)?";

            String baseDir = outdir + File.separator + nsp.replaceAll(pattern, "$2") + File.separator + prefix;
            //String thisDir = outdir + File.separator + nsp + File.separator + prefix;
            //String fileName = prefix.replaceAll(pattern, "$3").replaceAll("\\/|#", "_") + ".rdf";

            String pattern2 = "(https?://)?(.*?/)*(.*?.n3)(\\?.*)*";


            InputStream inputStream = null;
            OutputStream outputStream = null;

            try {

                for(String name : namesAndURLs.keySet()) {

                    String url = namesAndURLs.get(name);

                    String thisDir = baseDir + File.separator + name;
                    String fileName = url.replaceAll(pattern2, "$3");
                    new File(thisDir).mkdirs();

                    // read this file into InputStream
                    inputStream = getStream(url);


                    System.out.println("saving to " + thisDir + File.separator + fileName);

                    // write the inputStream to a FileOutputStream
                    outputStream =
                            new FileOutputStream(new File(thisDir + File.separator + fileName));

                    int read = 0;
                    byte[] bytes = new byte[1024];

                    while ((read = inputStream.read(bytes)) != -1) {
                        outputStream.write(bytes, 0, read);
                    }
                }

                System.out.println("Done!");

            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                if (inputStream != null) {
                    try {
                        inputStream.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
                if (outputStream != null) {
                    try {
                        // outputStream.flush();
                        outputStream.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }

                }
            }


        }


        logger.info("downloaded " + downloaded + " ontologies");
    }

}