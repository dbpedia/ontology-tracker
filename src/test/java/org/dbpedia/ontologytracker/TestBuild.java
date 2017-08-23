package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.enums.TestCaseExecutionType;
import org.aksw.rdfunit.io.reader.RdfDereferenceReader;
import org.aksw.rdfunit.io.reader.RdfReader;
import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.aksw.rdfunit.io.reader.RdfReaderFactory;
import org.aksw.rdfunit.model.interfaces.TestCase;
import org.aksw.rdfunit.model.interfaces.TestSuite;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.aksw.rdfunit.sources.TestSource;
import org.aksw.rdfunit.sources.TestSourceFactory;
import org.aksw.rdfunit.utils.TestUtils;
import org.aksw.rdfunit.validate.wrappers.RDFUnitStaticValidator;
import org.apache.jena.rdf.model.Model;

import java.util.ArrayList;
import java.util.Collection;

import static org.junit.Assert.fail;

public class TestBuild {

//    private final OntModel model;
    private static final String DBO_MANUAL_TESTS = "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbo.tests.Manual.ttl";
    private static final String DBPEDIA_ONTOLOGY = "http://rawgit.com/gcpdev/ontology-tracker/master/ontology/dbpedia_2016-10.owl";

    private RdfReader getDBpediaReader() {
        RdfReader readRDF = new RdfDereferenceReader(DBPEDIA_ONTOLOGY);
        return readRDF;
    }

    private TestSource getDBOSource() {
        return TestSourceFactory.createDumpTestSource("dbo", "http://dbpedia.org", getDBpediaReader(), new ArrayList<>());

    }

    private static TestSuite getDBpMappingsTestSuite() throws RdfReaderException {
        Collection<TestCase> tests = null;
        try {
            tests = TestUtils.instantiateTestsFromModel(
                    (Model) TestUtils.instantiateTestsFromModel(RdfReaderFactory.createResourceReader(DBO_MANUAL_TESTS).read()));
        } catch (Exception e) {
            fail("Cannot read resource: " + DBO_MANUAL_TESTS + ": " +
                    e.getCause());
        }

        return new TestSuite(tests);
    }

    /**
     * <p>validateAllMappings.</p>
     *
     * @return a {@link org.apache.jena.rdf.model.Model} object.
     * @throws RdfReaderException if any.
     */
    public TestExecution validateAllMappings() throws RdfReaderException {
        return RDFUnitStaticValidator.validate(TestCaseExecutionType.aggregatedTestCaseResult, getDBOSource(), getDBpMappingsTestSuite());
    }



}
