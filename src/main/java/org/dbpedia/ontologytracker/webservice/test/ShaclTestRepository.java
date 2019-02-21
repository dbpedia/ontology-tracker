package org.dbpedia.ontologytracker.webservice.test;

import org.dbpedia.ontologytracker.webservice.user.WebServiceUser;
import org.springframework.data.mongodb.repository.MongoRepository;
//import org.springframework.data.mongodb.repository.Query;
//import org.springframework.data.repository.query.Param;

//import org.springframework.data.jpa.repository.Query;
//import org.springframework.data.repository.CrudRepository;
//import org.springframework.data.repository.query.Param;

import java.util.List;


public interface ShaclTestRepository extends MongoRepository<ShaclTest, String> {

    List<ShaclTest> findByUser(WebServiceUser user);
    
    ShaclTest findByUserAndIdFromThisUser(WebServiceUser user, long idFromThisUser);

    void deleteByUserAndIdFromThisUser(WebServiceUser user, long idFromThisUser);
}