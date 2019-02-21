package org.dbpedia.ontologytracker.webservice;

import org.aksw.rdfunit.io.reader.RdfReaderException;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;

import javax.servlet.http.HttpServletRequest;

@ControllerAdvice
public class ServiceControllerExceptionHandler {

    @ResponseStatus(HttpStatus.BAD_REQUEST)  // 400
    @ExceptionHandler(value = {HttpMessageNotReadableException.class})
    @ResponseBody
    String
    handleEmptyRequest(HttpServletRequest req, Exception ex) {
        return "The ontology file could not be read by the server. Reason: " + System.lineSeparator() + ex.getLocalizedMessage() + System.lineSeparator();
    }

    @ResponseStatus(HttpStatus.BAD_REQUEST)  //400
    @ExceptionHandler(value = {RdfReaderException.class})
    @ResponseBody
    String
    handleWrongTestRequest(HttpServletRequest req, Exception ex) {
        return "RDFUnit could not run the specified tests. Reason: " + System.lineSeparator() + ex.getLocalizedMessage() + System.lineSeparator();
    }

    @ResponseStatus(HttpStatus.BAD_GATEWAY) // 500
    @ExceptionHandler(value = {ServiceController.class})
    @ResponseBody
    String
    handleFurtherExceptions(HttpServletRequest req, Exception ex) {
        return "The service could not handle your request due to a server error: " + System.lineSeparator() + ex.getLocalizedMessage() + System.lineSeparator();
    }
}
