package org.dbpedia.ontologytracker.webservice.authapi;

public class SecurityConstants {
    //public static final String SECRET = "SecretKeyToGenJWTs";
    public static final String SECRET = "SecretKeyToGenJWTs";
    public static final long EXPIRATION_TIME = 864_000_000; // 10 days
    public static final String TOKEN_PREFIX = "Bearer ";
    public static final String HEADER_STRING = "Authorization";
    public static final String SIGN_UP_URL = "/ws/users/sign-up";
    public static final String PUBLIC_ONTOLOGY = "/ws/ontology";
}