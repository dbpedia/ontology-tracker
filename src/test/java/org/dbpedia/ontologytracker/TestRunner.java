package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.io.reader.RdfModelReader;
import org.aksw.rdfunit.io.reader.RdfReader;
import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.aksw.rdfunit.io.reader.RdfReaderFactory;
import org.aksw.rdfunit.junit.RdfUnitJunitRunner;
import org.aksw.rdfunit.junit.Schema;
import org.aksw.rdfunit.junit.TestInput;
import org.junit.runner.RunWith;


@RunWith(RdfUnitJunitRunner.class)
@Schema(uri = "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbo.tests.shapes.ttl")
//@Schema(uri = "http://mappings.dbpedia.org/server/ontology/dbpedia.owl")
public class TestRunner {

    @TestInput
    public RdfReader getInputData() throws RdfReaderException {
        return new RdfModelReader(
                RdfReaderFactory.createResourceReader(
                        "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbpedia_2016-10.owl").read());
    }
    ;

}
