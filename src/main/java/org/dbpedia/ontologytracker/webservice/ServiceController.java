package org.dbpedia.ontologytracker.webservice;

import java.io.*;

import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.aksw.rdfunit.model.interfaces.results.TestExecution;
import org.aksw.rdfunit.model.writers.results.TestExecutionWriter;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.dbpedia.ontologytracker.RDFUnitValidate;
import org.dbpedia.ontologytracker.ValidateOntology;
import org.dbpedia.ontologytracker.webservice.test.ShaclTest;
import org.dbpedia.ontologytracker.webservice.test.ShaclTestRepository;
import org.dbpedia.ontologytracker.webservice.user.UserRepository;
import org.dbpedia.ontologytracker.webservice.user.WebServiceUser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.core.io.Resource;

@RestController
@RequestMapping("/ws")
public class ServiceController extends Exception {

    @Autowired
    private UserRepository userRepository;
    @Autowired
    private ShaclTestRepository shaclTestRepository;
	private static Logger L = LoggerFactory.getLogger(ServiceController.class);
	@Autowired
	private ApplicationContext applicationContext;
    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @PostMapping(value = {"/ontology"}, consumes = {"text/plain","text/turtle","application/x-turtle"},
            produces = {
                    "text/plain", //for returning errors strings
                    "text/turtle",
                    "application/x-turtle",
                    "application/ntriples",
                    "application/n-triples",
                    "application/jsonld",
                    "application/json-ld",
                    "application/json+ld",
                    "text/trig",
                    "text/nquads",
                    "application/rdfxml",
                    "application/rdf-xml",
                    "application/rdf+xml",
                    "application/rdfjson",
                    "application/rdf-json",
                    "application/rdf+json",
                    "text/trix",
                    "application/rdfthrft",
                    "application/rdf+thrift",
                    "application/rdfthrift" })
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public String ontology(@RequestBody byte[] file, @RequestHeader(value="Accept") String format) throws IOException, RdfReaderException {

        switch(format) {
            case "text/turtle":
            case "application/x-turtle":
                format = "TURTLE";
                break;
            case "application/ntriples":
            case "application/n-triples":
                format = "NTRIPLES";
                break;
            case "application/jsonld":
            case "application/json-ld":
            case "application/json+ld":
                format = "JSONLD";
                break;
            case "text/trig":
                format = "TRIG";
                break;
            case "text/nquads":
                format = "NQUADS";
                break;
            case "application/rdfxml":
            case "application/rdf-xml":
            case "application/rdf+xml":
                format = "RDFXML";
                break;
            case "application/rdfjson":
            case "application/rdf-json":
            case "application/rdf+json":
                format = "RDFJSON";
                break;
            case "text/trix":
                format = "TRIX";
                break;
            case "application/rdfthrft":
            case "application/rdf+thrift":
            case "application/rdfthrift":
                format = "RDFTHRIFT";
                break;
            default:
                format = "TURTLE";
        }

        try (InputStream is = new ByteArrayInputStream(file)) {
            Model model = ValidateOntology.readOntology(is);
            return ValidateOntology.runTests(model, format);
        }
    }

    /**
     * The following method can only be accessed by an authenticated user.
     * The testNumber parameter should be informed in the head of the requisition as "Test: x", where x is the number
     * of the custom test case of the authenticated user
     *
      * @param file
     * @param format
     * @param testNumber
     * @param authentication
     * @return
     * @throws IOException
     * @throws RdfReaderException
     */
    @PostMapping(value = {"/users/testOntology"}, consumes = {"text/plain","text/turtle","application/x-turtle"},
            produces = {
                    "text/plain", //for returning errors strings
                    "text/turtle",
                    "application/x-turtle",
                    "application/ntriples",
                    "application/n-triples",
                    "application/jsonld",
                    "application/json-ld",
                    "application/json+ld",
                    "text/trig",
                    "text/nquads",
                    "application/rdfxml",
                    "application/rdf-xml",
                    "application/rdf+xml",
                    "application/rdfjson",
                    "application/rdf-json",
                    "application/rdf+json",
                    "text/trix",
                    "application/rdfthrft",
                    "application/rdf+thrift",
                    "application/rdfthrift" })
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public String testOntology(@RequestBody byte[] file, @RequestHeader(value="Accept") String format, @RequestHeader(value="Test") int testNumber, Authentication authentication) throws IOException, RdfReaderException {

        switch(format) {
            case "text/turtle":
            case "application/x-turtle":
                format = "TURTLE";
                break;
            case "application/ntriples":
            case "application/n-triples":
                format = "NTRIPLES";
                break;
            case "application/jsonld":
            case "application/json-ld":
            case "application/json+ld":
                format = "JSONLD";
                break;
            case "text/trig":
                format = "TRIG";
                break;
            case "text/nquads":
                format = "NQUADS";
                break;
            case "application/rdfxml":
            case "application/rdf-xml":
            case "application/rdf+xml":
                format = "RDFXML";
                break;
            case "application/rdfjson":
            case "application/rdf-json":
            case "application/rdf+json":
                format = "RDFJSON";
                break;
            case "text/trix":
                format = "TRIX";
                break;
            case "application/rdfthrft":
            case "application/rdf+thrift":
            case "application/rdfthrift":
                format = "RDFTHRIFT";
                break;
            default:
                format = "TURTLE";
        }

        try (InputStream is = new ByteArrayInputStream(file)) {

            Model model = ValidateOntology.readOntology(is);

            String authUser = authentication.getName();

            WebServiceUser user = userRepository.findByUsername(authUser);

            ShaclTest shacl = shaclTestRepository.findByUserAndIdFromThisUser(user, testNumber);

            return ValidateOntology.runTests(model, format, shacl.getTest());
        }
    }

    // added by @asanchez75 for sending an URL ontology
    @PostMapping(value = {"/users/ontologyURL"}, consumes = {"text/plain"},
            produces = {
                    "text/plain", //for returning errors strings
                    "text/turtle",
                    "application/x-turtle",
                    "application/ntriples",
                    "application/n-triples",
                    "application/jsonld",
                    "application/json-ld",
                    "application/json+ld",
                    "text/trig",
                    "text/nquads",
                    "application/rdfxml",
                    "application/rdf-xml",
                    "application/rdf+xml",
                    "application/rdfjson",
                    "application/rdf-json",
                    "application/rdf+json",
                    "text/trix",
                    "application/rdfthrft",
                    "application/rdf+thrift",
                    "application/rdfthrift" })
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public String ontologyURL(@RequestBody String url, @RequestHeader(value="Accept") String format) throws IOException, RdfReaderException {

        switch(format) {
            case "text/turtle":
            case "application/x-turtle":
                format = "TURTLE";
                break;
            case "application/ntriples":
            case "application/n-triples":
                format = "NTRIPLES";
                break;
            case "application/jsonld":
            case "application/json-ld":
            case "application/json+ld":
                format = "JSONLD";
                break;
            case "text/trig":
                format = "TRIG";
                break;
            case "text/nquads":
                format = "NQUADS";
                break;
            case "application/rdfxml":
            case "application/rdf-xml":
            case "application/rdf+xml":
                format = "RDFXML";
                break;
            case "application/rdfjson":
            case "application/rdf-json":
            case "application/rdf+json":
                format = "RDFJSON";
                break;
            case "text/trix":
                format = "TRIX";
                break;
            case "application/rdfthrft":
            case "application/rdf+thrift":
            case "application/rdfthrift":
                format = "RDFTHRIFT";
                break;
            default:
                format = "TURTLE";
        }
    	    Resource resource = applicationContext.getResource(url);
        try (InputStream is = resource.getInputStream()) {        	
            Model model = ValidateOntology.readOntology(is);
            return ValidateOntology.runTests(model, format);
        }
    }
    
    // added by @asanchez75 for uploading two files
    @RequestMapping(value = "/users/ontologyUpload", method = RequestMethod.POST, consumes = {"multipart/form-data"},  headers = {"content-type=multipart/mixed","content-type=multipart/form-data"})    
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public String ontologyUpload(@RequestPart(value="ontology") MultipartFile ontology, @RequestPart(value="shacltest") MultipartFile shacltest, @RequestParam(value="format") String format, Authentication authentication) throws IOException, RdfReaderException {
    	 
    	    L.info("Multiple file upload!");
        
    	    String out = "";
            
        switch(format) {
            case "text/turtle":
            case "application/x-turtle":
                format = "TURTLE";
                break;
            case "application/ntriples":
            case "application/n-triples":
                format = "NTRIPLES";
                break;
            case "application/jsonld":
            case "application/json-ld":
            case "application/json+ld":
                format = "JSONLD";
                break;
            case "text/trig":
                format = "TRIG";
                break;
            case "text/nquads":
                format = "NQUADS";
                break;
            case "application/rdfxml":
            case "application/rdf-xml":
            case "application/rdf+xml":
                format = "RDFXML";
                break;
            case "application/rdfjson":
            case "application/rdf-json":
            case "application/rdf+json":
                format = "RDFJSON";
                break;
            case "text/trix":
                format = "TRIX";
                break;
            case "application/rdfthrft":
            case "application/rdf+thrift":
            case "application/rdfthrift":
                format = "RDFTHRIFT";
                break;
            default:
                format = "TURTLE";
        }
        

        try  {
        	
            InputStream isontol = ontology.getInputStream();
            InputStream isshacl = shacltest.getInputStream();

            /*if(inputStreamToString(isontol).isEmpty()){
                L.error("Error: ontology file is empty");
                //return "Error: ontology file is empty";
            }
            if(inputStreamToString(isshacl).isEmpty()){
                L.error("Error: SHACL file is empty");
                //return "Error: SHACL file is empty";
            }*/
            
            Model model = ValidateOntology.readOntology(isontol);

            out = ValidateOntology.runShaclTests(model, inputStreamToString(isshacl));
            /*RDFUnitValidate rval = new RDFUnitValidate(isshacl);
            
            TestExecution te = rval.checkModelWithRdfUnit(model);

            try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                Model resultModel = ModelFactory.createDefaultModel();
                TestExecutionWriter.create(te).write(resultModel);
                resultModel.write(baos, format);

                out = baos.toString();

            } catch (IOException e) {
                e.printStackTrace();
                out = "An error occurred while writing tests output.";
            }*/


        } 

        catch (Exception e) {
            L.info("An error occurred while uploading ontology and shacl tests files: " + e.getMessage());
        }
        L.info(out);
        return out;
    }

    private String inputStreamToString(InputStream inputStream) {
        String output = "";
        ByteArrayOutputStream result = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        int length;
        try {
            while ((length = inputStream.read(buffer)) != -1) {
                result.write(buffer, 0, length);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            output = result.toString("UTF-8");
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        return output;
    }
}
