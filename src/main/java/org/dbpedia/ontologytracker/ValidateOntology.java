package org.dbpedia.ontologytracker;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.aksw.rdfunit.model.interfaces.results.ShaclTestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.aksw.rdfunit.model.writers.results.TestExecutionWriter;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.log4j.Logger;

import java.io.*;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

public class ValidateOntology {
    private static long startTime = System.currentTimeMillis();

    private static Logger L = Logger.getLogger(ValidateOntology.class);

    private static final File DBPEDIA_ONTOLOGY = new File("ontology/dbpedia_ontology.ttl");
    private static final String baseUri = "http://dbpedia.org/ontology/";
    private static String outdir = "result";

    /**
     * @param is The InputStream of the ontology file
     *
     * @return The ontology read as a jena Model
     */
    public static Model readOntology(InputStream is) throws IOException {

        Model model = ModelFactory.createDefaultModel();

        try {
            model.read(is, baseUri, "TTL");
        } catch (Exception e) {
            L.error("Error processing file: " + e.getMessage());
        }
        return model;
    }

    /**
     * @param is The InputStream of the ontology file
     * @param format String with the input format of the ontology file ("TTL", "RDF/XML", etc.)
     *
     * @return The ontology read as a jena Model
     */
    public static Model readOntology(InputStream is, String format) throws IOException {

        Model model = ModelFactory.createDefaultModel();

        try {
            model.read(is, format);
        } catch (Exception e) {
            L.error("Error processing file: " + e.getMessage());
        }
        return model;
    }

    /**
     * @param model The jena Model of the ontology file
     *
     * @return A Collection of ShaclTestCaseResult
     */
    public static Collection<ShaclTestCaseResult> runShaclTests(Model model) {
        RDFUnitValidate rval = new RDFUnitValidate();
        TestExecution te = rval.checkModelWithRdfUnit(model);

        Collection<TestCaseResult> tcrs = te.getTestCaseResults();
        Collection<ShaclTestCaseResult> stcrs = new ArrayList<>();

        tcrs.forEach(tcr -> {
            stcrs.add((ShaclTestCaseResult) tcr);
        });
        return stcrs;
    }

    /**
     * @param model The jena Model of the ontology file
     * @param test String with custom SHACL test to be run against the Model
     *
     * @return The test results as a JSON string
     */
    public static String runShaclTests(Model model, String test) {
        RDFUnitValidate rval = new RDFUnitValidate(test);
        TestExecution te = rval.checkModelWithRdfUnit(model);

        Collection<TestCaseResult> tcrs = te.getTestCaseResults();
        Collection<ShaclTestCaseResult> stcrs = new ArrayList<>();

        tcrs.forEach(tcr -> {
            stcrs.add((ShaclTestCaseResult) tcr);
        });

        List<DBpediaTestResult> tests = new ArrayList<>();
        stcrs.stream().forEach(t -> {
            //logging
            //L.info(t.getSeverity().name() + " " + t.getMessage() + " " + t.getFailingResource());
            tests.add(new DBpediaTestResult(t));

        });

        Gson gson = new GsonBuilder().disableHtmlEscaping().create();

        return gson.toJson(tests).replace("\\\\", "\\");
    }

    /**
     * @param model The jena Model of the ontology file
     * @param test String with custom SHACL test to be run against the Model
     *
     * @return The test results as a JSON string
     */
    public static List<DBpediaTestResult> returnShaclTests(Model model, String test) {
        RDFUnitValidate rval = new RDFUnitValidate(test);
        TestExecution te = rval.checkModelWithRdfUnit(model);

        Collection<TestCaseResult> tcrs = te.getTestCaseResults();
        Collection<ShaclTestCaseResult> stcrs = new ArrayList<>();

        tcrs.forEach(tcr -> {
            stcrs.add((ShaclTestCaseResult) tcr);
        });

        List<DBpediaTestResult> tests = new ArrayList<>();
        stcrs.stream().forEach(t -> {
            //logging
            //L.info(t.getSeverity().name() + " " + t.getMessage() + " " + t.getFailingResource());
            tests.add(new DBpediaTestResult(t));

        });

        return tests;
    }

    /**
     * @param model The jena Model of the ontology file
     * @param format String with the expected output format
     *
     * @return The test results as a string in the specified format
     */
    public static String runTests(Model model, String format) {

        RDFUnitValidate rval = new RDFUnitValidate();
        TestExecution te = rval.checkModelWithRdfUnit(model);
        String out = "";

        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            Model resultModel = ModelFactory.createDefaultModel();
            TestExecutionWriter.create(te).write(resultModel);
            resultModel.write(baos, format);

            out = baos.toString();

        } catch (IOException e) {
            e.printStackTrace();
            out = "An error occurred while writing tests output.";
        }

        return out;

    }

    /**
     * @param model The jena Model of the ontology file
     * @param format String with the expected output format
     * @param test String with custom SHACL test to be run against the Model
     *
     * @return The test results as a string in the specified format
     */
    public static String runTests(Model model, String format, String test) {

        RDFUnitValidate rval = new RDFUnitValidate(test);
        TestExecution te = rval.checkModelWithRdfUnit(model);
        String out = "";

        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            Model resultModel = ModelFactory.createDefaultModel();
            TestExecutionWriter.create(te).write(resultModel);
            resultModel.write(baos, format);

            out = baos.toString();

        } catch (IOException e) {
            e.printStackTrace();
            out = "An error occurred while writing tests output.";
        }


        return out;

    }

    public static void main(String[] args) throws IOException {

        new File(outdir).mkdirs();

        InputStream is = new FileInputStream(DBPEDIA_ONTOLOGY);

        Model model = readOntology(is); // reads DBpedia Ontology
        L.debug("Read model: " + model.size() + " triples");

        Collection<ShaclTestCaseResult> tcrs = runShaclTests(model);
        L.debug("Tests finished");

        List<DBpediaTestResult> tests = new ArrayList<>();
        tcrs.stream().forEach(t -> {
            //logging
            //L.info(t.getSeverity().name() + " " + t.getMessage() + " " + t.getFailingResource());
            tests.add(new DBpediaTestResult(t));

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