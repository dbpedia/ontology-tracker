package org.dbpedia.ontologytracker;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.rdf.model.Model;
import org.apache.log4j.Logger;

import java.io.ByteArrayOutputStream;

public class DBpediaTest {
    public String level;
    public String message;
    static JsonElement modelasjson;

    private DBpediaTest(String level, String message) {
        this.level = level;
        this.message = message;
    }

    /**
     * no logging
     * @param level
     * @param message
     * @return
     */
    public static DBpediaTest create(String level, String message ){
        level = level.toUpperCase();

        return new DBpediaTest(level,message);
    }

    /**
     * logging
     *
     * @param level
     * @param message
     * @param L
     * @param e
     * @return
     */

    public static DBpediaTest create(String level, String message, Logger L, Exception e  ){
        level = level.toUpperCase();
        String issueMessage = (e==null)? message : message+"- Error: "+e.toString() ;
        if (level.equals("WARN")) {
            if(e==null){L.warn(message);}else{L.warn(message,e);}
        } else if (level.equals("ERROR")) {
            if(e==null){L.error(message);}else{L.error(message,e);}
        } else if (level.equals("INFO")){
            if(e==null){L.info(message);}else{L.info(message,e);}
        }else{
            L.error("Level "+level+" not implemented in org.dbpedia.ontologytracker.Issue");
        }
        return new DBpediaTest(level,issueMessage);
    }

    public void prepareJSON(org.apache.jena.ontology.OntModel model) {
        Gson gson = new Gson();
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        model.write(baos, "RDF/JSON");
        modelasjson = gson.fromJson(new String(baos.toByteArray(), java.nio.charset.StandardCharsets.UTF_8), JsonElement.class);
    }

    @Override
    public String toString() {
        return "Issue{" +
                "level='" + level + '\'' +
                ", message='" + message + '\'' +
                '}';
    }
}
