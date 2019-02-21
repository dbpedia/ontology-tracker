package org.dbpedia.ontologytracker;

import java.io.InputStream;

import org.aksw.rdfunit.enums.TestCaseExecutionType;
import org.aksw.rdfunit.io.reader.RdfModelReader;
import org.aksw.rdfunit.io.reader.RdfReader;
import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.aksw.rdfunit.io.reader.RdfReaderFactory;
import org.aksw.rdfunit.io.reader.RdfStreamReader;
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
    static String defaultSchema = "ontology/dbo.tests.shapes.ttl";
    private static Logger L = Logger.getLogger(RDFUnitValidate.class);

    public RDFUnitValidate() {
        this(defaultSchema);
    }
    
    public RDFUnitValidate(String schemaSource) {
        long startTime = System.nanoTime();
        RdfReader ontologyShaclReader = null;
        try {
            if(schemaSource != defaultSchema)
                ontologyShaclReader = new RdfModelReader(RdfReaderFactory.createReaderFromText(schemaSource, "TTL").read());
            else
                ontologyShaclReader = new RdfModelReader(RdfReaderFactory.createFileOrResourceReader(schemaSource, "").read());
        } catch (RdfReaderException e) {
            throw new IllegalArgumentException(e);
        }
        SchemaSource ontologyShaclSource = SchemaSourceFactory.createSchemaSourceSimple("tests", "http://rdfunit.aksw.org", ontologyShaclReader);
        this.ts = new TestSuite(new ShaclTestGenerator().generate(ontologyShaclSource));
        long endTime = System.nanoTime();
        L.debug("Generated "+ts.getTestCases().size() + " test cases in " + (endTime - startTime) / 1000000 + " ms");
    }

    public RDFUnitValidate(InputStream file) {
        long startTime = System.nanoTime();
        RdfReader ontologyShaclReader = null;
        try {
          	ontologyShaclReader = new RdfModelReader(new RdfStreamReader(file, "TURTLE").read());
            
        } catch (RdfReaderException e) {
            throw new IllegalArgumentException(e);
        }
        SchemaSource ontologyShaclSource = SchemaSourceFactory.createSchemaSourceSimple("tests", "http://rdfunit.aksw.org", ontologyShaclReader);
        this.ts = new TestSuite(new ShaclTestGenerator().generate(ontologyShaclSource));
        long endTime = System.nanoTime();
        L.debug("Generated "+ts.getTestCases().size() + " test cases in " + (endTime - startTime) / 1000000 + " ms");
    }
    
    public TestExecution checkModelWithRdfUnit(Model model) {
        return RDFUnitStaticValidator.validate(TestCaseExecutionType.shaclFullTestCaseResult, model, this.ts);
    }


}
