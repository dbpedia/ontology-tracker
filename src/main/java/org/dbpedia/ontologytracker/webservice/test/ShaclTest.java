package org.dbpedia.ontologytracker.webservice.test;

import org.dbpedia.ontologytracker.webservice.user.WebServiceUser;
import org.springframework.data.mongodb.core.mapping.DBRef;

import javax.persistence.Entity;
import javax.persistence.Id;

@Entity
public class ShaclTest {

    @Id
    private long idFromThisUser = 1;

    private String test;

    @DBRef
    private WebServiceUser user;

    public ShaclTest() {}

    public ShaclTest(String test, WebServiceUser user) {
        this.setTest(test);
        this.setUser(user);
    }

    public String getTest() {
        return test;
    }

    public void setTest(String test) {
        this.test = test;
    }

    public WebServiceUser getUser() {
        return user;
    }

    public void setUser(WebServiceUser user) {
        this.user = user;
    }

    public ShaclTest getShaclTest(long id) {
        return new ShaclTest(test, user);
    }

    public long getIdFromThisUser() {
        return idFromThisUser;
    }

    public void setIdFromThisUser(long idFromThisUser) {
        this.idFromThisUser = idFromThisUser;
    }
}
