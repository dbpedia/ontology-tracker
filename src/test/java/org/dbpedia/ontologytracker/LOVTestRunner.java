package org.dbpedia.ontologytracker;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Iterator;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

@SpringBootApplication
public class LOVTestRunner implements CommandLineRunner {

    public final String repositoryAddress = "http://lov.okfn.org/dataset/lov/api/v2/vocabulary/list";

    public static Logger logger = LoggerFactory.getLogger(LOVTestRunner.class);

    public static void main(String[] args) {
        SpringApplication.run(LOVTestRunner.class, args).close();
    }

    @Autowired
    private KafkaTemplate<String, String> template;

    private final CountDownLatch latch = new CountDownLatch(3);

    public void parse() {
        //URI uri;
        try {
            //uri = new URI(repositoryAddress);
            JSONTokener tokener = new JSONTokener(new URL(repositoryAddress).openStream());
            JSONArray root = new JSONArray(tokener);

            Iterator<Object> it = root.iterator();
            while (it.hasNext()) {
                //streamAndRunTests((JSONObject) it.next());
                this.template.send("myTopic", ((JSONObject) it.next()).get("uri").toString());
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /**
     * Open a connection and return the stream
     * @param downloadURL
     * @param accept
     * @return
     * @throws IOException
     */
    public InputStream getStream(String downloadURL, String accept) throws IOException {
        HttpURLConnection httpConn;
        httpConn = (HttpURLConnection) new URL(downloadURL).openConnection();
        httpConn.setReadTimeout(114000);
        httpConn.setConnectTimeout(114000);
        if (accept != null)
            httpConn.setRequestProperty("Accept", accept);
        else
            httpConn.setRequestProperty("Accept", "application/rdf+xml");

        return new BufferedInputStream(httpConn.getInputStream());
    }


    /**
     * Save a LOV Vocabulary or ontology instance the main collection
     *
     * @param url
     * @return test results
     */
    public void streamAndRunTests(String url) {

        //String title = ((JSONObject) ((JSONArray) object.get("titles")).get(0)).get("value").toString();
        //String url = object.get("uri").toString();

        //DatasetDB dataset = addDataset(url, true, title, title, getParserName());

        logger.info("Running tests on "+url);

        //saveDistribution(url, title, dataset);

        //return title;
    }


    @Override
    public void run(String... args) throws Exception {
		/*this.template.send("myTopic", "foo1");
		this.template.send("myTopic", "foo2");
		this.template.send("myTopic2", "foo3");*/
        parse();
        latch.await(60, TimeUnit.SECONDS);
        logger.info("All received");
    }

    @KafkaListener(topics = "myTopic")
    public void listen(ConsumerRecord<?, ?> cr) throws Exception {
        logger.info("myTopic sent URL "+cr.toString());
        streamAndRunTests(cr.toString());
        latch.countDown();
    }

    @KafkaListener(topics = "myTopic2")
    public void listen2(ConsumerRecord<?, ?> cr) throws Exception {
        logger.info("mytopic porraa!"+cr.toString());
        latch.countDown();
    }

}