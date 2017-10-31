package org.dbpedia.ontologytracker.webservice.user;

import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import static java.util.Collections.emptyList;

@Service
public class UserDetailsServiceImpl implements UserDetailsService {
    private UserRepository userRepository;

    public UserDetailsServiceImpl(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        WebServiceUser webServiceUser = userRepository.findByUsername(username);
        if (webServiceUser == null) {
            throw new UsernameNotFoundException(username);
        }
        return new User(webServiceUser.getUsername(), webServiceUser.getPassword(), emptyList());
    }
}