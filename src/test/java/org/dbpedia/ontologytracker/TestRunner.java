package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.io.reader.RdfModelReader;
import org.aksw.rdfunit.io.reader.RdfReader;
import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.aksw.rdfunit.io.reader.RdfReaderFactory;
import org.aksw.rdfunit.junit.RdfUnitJunitRunner;
import org.aksw.rdfunit.junit.Schema;
import org.aksw.rdfunit.junit.TestInput;
import org.junit.runner.RunWith;
import org.aksw.rdfunit.utils.UriToPathUtils;


@RunWith(RdfUnitJunitRunner.class)
@Schema(uri = "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbo.tests.shapes.ttl")
public class TestRunner {

    @TestInput
    public RdfReader getInputData() throws RdfReaderException {
        return new RdfModelReader(
                RdfReaderFactory.createResourceReader(
                        //"http://rawgit.com/gcpdev/ontology-tracker/master/ontology/dbpedia_2016-10.owl").read());
                        "/org/aksw/rdfunit/tests/Manual/dbpedia.org/ontology/dbpedia_2016-10.owl").read());
    }
    ;

}
