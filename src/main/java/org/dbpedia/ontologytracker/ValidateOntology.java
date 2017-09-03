package org.dbpedia.ontologytracker;

import com.google.gson.Gson;
import org.aksw.rdfunit.model.interfaces.results.ShaclTestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.log4j.Logger;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

public class ValidateOntology {
    private static long startTime = System.currentTimeMillis();

    private static Logger L = Logger.getLogger(ValidateOntology.class);


    //private static final String DBO_MANUAL_TESTS = "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbo.tests.Manual.ttl";
    private static final File DBPEDIA_ONTOLOGY = new File("ontology/dbpedia_2016-10.ttl");
    private static final String baseUri = "http://dbpedia.org/ontology/";
    private static String outdir = "result";


    private static Model readDBpediaOntology() throws IOException {

        //OntModel model = ModelFactory.createOntologyModel();
        Model model = ModelFactory.createDefaultModel();

        try {
            RDFDataMgr.read(model, DBPEDIA_ONTOLOGY.toURI().toString(), baseUri, Lang.TURTLE);
        } catch (Exception e) {
            L.error(e.getMessage());
        }
        return model;
    }

    private static Collection<ShaclTestCaseResult> runTests(Model model) {
        RDFUnitValidate rval = new RDFUnitValidate();
        TestExecution te = rval.checkModelWithRdfUnit(model);

        Collection<TestCaseResult> tcrs = te.getTestCaseResults();
        Collection<ShaclTestCaseResult> stcrs = new ArrayList<>();

        tcrs.forEach(tcr -> {
            stcrs.add((ShaclTestCaseResult) tcr);
        });
        return stcrs;
    }

    public static void main(String[] args) throws IOException {

        new File(outdir).mkdirs();

        Model model = readDBpediaOntology();
        L.debug("Read model: " + model.size() + " triples");

        Collection<ShaclTestCaseResult> tcrs = runTests(model);
        L.debug("Tests finished");

        List<DBpediaTest> tests = new ArrayList<>();
        tcrs.stream().forEach(t -> {
            //logging
            //L.info(t.getSeverity().name() + " " + t.getMessage() + " " + t.getFailingResource());
            tests.add(new DBpediaTest(t));

        });


        FileWriter fw = new FileWriter(outdir + File.separator + "data.json");
        new Gson().toJson(tests, fw);
        fw.close();
        L.info("wrote json to " + outdir + File.separator + "data.json");


        long endTime = System.currentTimeMillis();
        long totalTime = (endTime - startTime) / 1000;
        L.info("Program execution ended, " + tcrs.size() + " issues. Total execution time of Java code: " + totalTime + " seconds");


    }

}