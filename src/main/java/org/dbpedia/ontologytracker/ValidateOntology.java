package org.dbpedia.ontologytracker;

import com.google.gson.Gson;
import org.aksw.rdfunit.model.interfaces.results.ShaclTestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.apache.jena.ontology.OntModel;
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

    private static Logger L = Logger.getLogger(ValidateOntology.class);

    //private static final String DBO_MANUAL_TESTS = "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbo.tests.Manual.ttl";
    private static final String DBPEDIA_ONTOLOGY = "http://rawgit.com/gcpdev/ontology-tracker/master/ontology/dbpedia_2016-10.owl";
    private static OntModel model = null;
    private static String outdir = "/home/gpublio/ontology-tracker/";

    private static List<org.dbpedia.ontologytracker.Issue> issues = new ArrayList<>();

    private static void readOntology(File file) throws IOException {

        String baseUri = file.getParentFile().getCanonicalFile().toURI() + file.getName() + "#";
        model = ModelFactory.createOntologyModel();
        //Metadata m = new Metadata(file, baseUri, model);

        try {
            RDFDataMgr.read(model, file.toURI().toString(), baseUri, Lang.TURTLE);
        } catch (Exception e) {
            //m.issues.add( Issue.create("ERROR", "Error when parsing " + m.reponame + "/" + m.nicename + "/metadata.ttl, skipping",L,e));
            //return m;
        }

    }

    private static void runTests(RDFUnitValidate rval) {

        TestExecution te = rval.checkModelWithRdfUnit(model);
        Collection<TestCaseResult> tcrs = te.getTestCaseResults();
        tcrs.forEach(tcr ->
                issues.add(Issue.create(tcr.getSeverity().name(), tcr.getMessage()+" "+((ShaclTestCaseResult)tcr).getFailingResource(),L,null)));
    }

    public static void main(String[] args) throws IOException {

        RDFUnitValidate rval = new RDFUnitValidate();
        File file = new File(DBPEDIA_ONTOLOGY);
        readOntology(file);
        runTests(rval);

        issues.stream().forEach((org.dbpedia.ontologytracker.Issue i) -> {
            i.prepareJSON(model);
        });

        FileWriter fw = new FileWriter(outdir + File.separator + "data.json");
        new Gson().toJson(issues, fw);
        fw.close();
        L.info("wrote json to " + outdir + File.separator + "data.json");

    }

}