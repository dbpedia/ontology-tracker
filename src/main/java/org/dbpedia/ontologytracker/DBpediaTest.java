package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.model.interfaces.results.ShaclTestCaseResult;

import java.util.HashSet;
import java.util.Set;

public class DBpediaTest {
    public String level;
    public String message;
    public String testcaseuri;
    public String failingresource;
    public Set<String> propertyValuepairs = new HashSet<>();

    public DBpediaTest(ShaclTestCaseResult stcr) {
        level = stcr.getSeverity().name();
        message = stcr.getMessage();
        failingresource = stcr.getFailingResource();
        testcaseuri = stcr.getTestCaseUri();
        level = stcr.getResultAnnotations().toString();
        stcr.getResultAnnotations().forEach(p -> {
            propertyValuepairs.add(p.toString());
        });
    }
}
