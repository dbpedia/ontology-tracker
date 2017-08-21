package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.enums.TestCaseExecutionType;
import org.aksw.rdfunit.model.interfaces.TestCase;
import org.aksw.rdfunit.model.interfaces.results.TestCaseResult;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.aksw.rdfunit.validate.wrappers.RDFUnitStaticValidator;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assert.assertNotEquals;


@RunWith(Parameterized.class)
public class TestBuild {

//    private final OntModel model;
    TestCaseResult tcr;


    public TestBuild(TestCaseResult tcr) {
        this.tcr = tcr;
    }

    @Parameterized.Parameters
    public static List<TestCaseResult> testNumbers() {
        OntModel model = ModelFactory.createOntologyModel();


        try {
            RDFDataMgr.read(model, "", "", Lang.TURTLE);
        } catch (Exception e) {
            e.printStackTrace();
        }

        //TODO
        TestExecution te = RDFUnitStaticValidator.validate(null, null, "");

        List<TestCaseResult> tcrs = new ArrayList<>();
        tcrs.addAll( te.getTestCaseResults());
        return tcrs;
    }

    @Test
    public void checkIssuesForError() {
           assertNotEquals(tcr.getMessage(),tcr.getSeverity().name(),"ERROR");
    }

}
