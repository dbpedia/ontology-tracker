package org.dbpedia.ontologytracker;

import org.aksw.rdfunit.model.helper.PropertyValuePair;
import org.aksw.rdfunit.model.interfaces.results.ShaclTestCaseResult;

import java.util.HashSet;
import java.util.Set;

public class DBpediaTest {
    public String level;
    public String message;
    public String testcaseuri;
    public String failingresource;
    public Set<PV> propertyValuePairs = new HashSet<>();

    public class PV {
        public String property;
        public Set<String> values = new HashSet<>();

        public PV(PropertyValuePair p) {
            this.property = p.getProperty().toString();
            p.getValues().forEach(v -> {
                this.values.add(v.toString());
            });
        }
    }

    public DBpediaTest(ShaclTestCaseResult stcr) {
        level = stcr.getSeverity().name();
        message = stcr.getMessage();
        //failingresource = stcr.getFailingResource();
        testcaseuri = stcr.getTestCaseUri();
        //level = stcr.getSeverity().toString(); // this does not work, as it only returns RLOG = ERROR
        level = stcr.getResultAnnotations().toString();
        stcr.getResultAnnotations().forEach(p -> {
            if(p.getProperty().toString().compareTo("http://www.w3.org/ns/shacl#focusNode") == 0)
                p.getValues().forEach(v -> {
                    failingresource = v.toString();
                });
            propertyValuePairs.add(new PV(p));
        });
    }
}
