package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.enums.TestCaseExecutionType;
import org.aksw.rdfunit.io.reader.RdfModelReader;
import org.aksw.rdfunit.io.reader.RdfReader;
import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.aksw.rdfunit.io.reader.RdfReaderFactory;
import org.aksw.rdfunit.model.interfaces.TestSuite;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.aksw.rdfunit.sources.SchemaSource;
import org.aksw.rdfunit.sources.SchemaSourceFactory;
import org.aksw.rdfunit.tests.generators.ShaclTestGenerator;
import org.aksw.rdfunit.validate.wrappers.RDFUnitStaticValidator;
import org.apache.jena.rdf.model.Model;
import org.apache.log4j.Logger;

public class RDFUnitValidate {

    TestSuite ts = null;
    static String defaultSchema = "/dbo.tests.shapes.ttl";
    private static Logger L = Logger.getLogger(RDFUnitValidate.class);

    public RDFUnitValidate() {
        this(defaultSchema);
    }

    public RDFUnitValidate(String schemaSource) {
        RdfReader ontologyShaclReader = null;
        try {
            ontologyShaclReader = new RdfModelReader(RdfReaderFactory.createResourceReader(schemaSource).read());
        } catch (RdfReaderException e) {
            throw new IllegalArgumentException(e);
        }
        SchemaSource ontologyShaclSource = SchemaSourceFactory.createSchemaSourceSimple("tests", "http://rdfunit.aksw.org", ontologyShaclReader);
        this.ts = new TestSuite(new ShaclTestGenerator().generate(ontologyShaclSource));
        L.debug("Generated "+ts.getTestCases().size() + " test cases");
    }

    public TestExecution checkModelWithRdfUnit(Model model) {
        return RDFUnitStaticValidator.validate(TestCaseExecutionType.shaclFullTestCaseResult, model, this.ts);
    }


}
