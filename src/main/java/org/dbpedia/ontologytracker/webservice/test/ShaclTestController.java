package org.dbpedia.ontologytracker.webservice.test;

import org.dbpedia.ontologytracker.webservice.user.UserRepository;
import org.dbpedia.ontologytracker.webservice.user.WebServiceUser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.Assert;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Comparator;
import java.util.List;

@RestController
@RequestMapping("/tests/{username}")
public class ShaclTestController {

    @Autowired
    private UserRepository userRepository;

    private ShaclTestRepository shaclTestRepository;

    public ShaclTestController(ShaclTestRepository shaclTestRepository) {
        this.shaclTestRepository = shaclTestRepository;
    }

    @PostMapping
    public void addShaclTest(@PathVariable String username, @RequestBody String test) {
        WebServiceUser user = userRepository.findByUsername(username);
        ShaclTest shaclTest = new ShaclTest(test, user);
        try {
            shaclTestRepository.save(shaclTest);
        }
        catch (org.springframework.dao.DuplicateKeyException e) {
            List<ShaclTest> tests = shaclTestRepository.findByUser(user);
            tests.sort(Comparator.comparing(ShaclTest::getIdFromThisUser));
            ShaclTest newestTest = tests.get(tests.size()-1);
            shaclTest.setIdFromThisUser(newestTest.getIdFromThisUser() + 1);
            shaclTestRepository.save(shaclTest);
        }
    }

    @GetMapping
    public List<ShaclTest> getUserShaclTests(@PathVariable String username) {
        WebServiceUser user = userRepository.findByUsername(username);
        return shaclTestRepository.findByUser(user);
    }

    @PutMapping("/{idFromThisUser}")
    public void editShaclTest(@PathVariable String username, @PathVariable long idFromThisUser, @RequestBody ShaclTest test) {
        WebServiceUser user = userRepository.findByUsername(username);
        ShaclTest existingShaclTest = shaclTestRepository.findByUserAndIdFromThisUser(user, idFromThisUser);
        Assert.notNull(existingShaclTest, "ShaclTest not found");
        existingShaclTest.setTest(test.getTest());
        shaclTestRepository.save(existingShaclTest);
    }

    @DeleteMapping("/{idFromThisUser}")
    public void deleteShaclTest(@PathVariable String username, @PathVariable long idFromThisUser) {
        WebServiceUser user = userRepository.findByUsername(username);
        shaclTestRepository.deleteByUserAndIdFromThisUser(user, idFromThisUser);
    }
}