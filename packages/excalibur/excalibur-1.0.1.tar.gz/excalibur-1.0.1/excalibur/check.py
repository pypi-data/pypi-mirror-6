# -*- coding: utf-8 -*-
import hashlib
import re

from excalibur.exceptions import ArgumentError, ArgumentCheckMethodNotFoundError, CheckMethodError,\
    NoACLMatchedError, RessourceNotFoundError, MethodNotFoundError, HTTPMethodError, SourceNotFoundError, \
    IPNotAuthorizedError, WrongSignatureError


class Check(object):

    """
    Classe mere pour implementer les Checks.
    """

    def check(self):
        raise NotImplementedError


class CheckArguments(Check):

    """
    Classe verifiant la consistance des arguments.

    Pour implementer un nouveau test, il suffit d'implementer une nouvelle methode qui
    doit se nommer check_nomdutest. Les arguments passes doivent etre la valeur a tester
    et une valeur servant au test. La valeur de retour doit etre un booleen.
    """

    def __init__(self,query, ressources):
        self.ressources = ressources
        self.arguments = query.arguments
        self.ressource = query.ressource
        self.method = query.method
        
    def __call__(self):
        errors = {}  # Garde la trace des arguments qui ont echoue aux checks
        for argument_name in self.arguments:
            # Construction et verification de la batterie de checks
            # (check_list)
            try:
                check_list = self.ressources[self.ressource][self.method][
                    "arguments"][argument_name]["checks"]
            except KeyError:
                raise ArgumentError("unexpected argument %s" % argument_name)

            for check in check_list:
                try:
                    check_method_name = "check_" + check.replace(" ", "_")
                    check_method = getattr(self, check_method_name)
                    check_parameter = self.ressources[self.ressource][self.method][
                        "arguments"][argument_name]["checks"][check]
                    value_to_check = self.arguments[argument_name]

                    if not check_method(value_to_check, check_parameter):
                        errors[argument_name] = check
                except AttributeError:
                    raise ArgumentCheckMethodNotFoundError(check_method_name)
                except Exception as e:
                    # Erreur dans la 'check method'
                    raise CheckMethodError(e)

        if errors:
            raise ArgumentError("The check list did not pass", errors)

    def check_min_length(self, argument_value, length):
        return len(argument_value) >= length

    def check_max_length(self, argument_value, length):
        return len(argument_value) <= length

    def check_value_in(self, argument_value, choices):
        return argument_value in choices

    def check_matches_re(self, argument_value, re_string):
        regex = re.compile(re_string)

        return regex.match(argument_value) is not None


class CheckACL(Check):

    """
    Verifie les acces aux ressources et methodes. Les ACL sont definies dans
    le fichier acl.yml.
    """

    def __init__(self,query, acl):
        self.acl = acl
        self.source = query.source
        self.ressource = query.ressource
        self.method = query.method
        self.project = query.project

    def __call__(self):
        try:
            if self.project:
                if self.method not in self.acl[self.project][self.source][self.ressource]:
                    raise NoACLMatchedError("%s/%s" % (self.ressource, self.method))
            else:
                if self.method not in self.acl[self.source][self.ressource]:
                    raise NoACLMatchedError("%s/%s" % (self.ressource, self.method))
        except KeyError:
            raise NoACLMatchedError("%s/%s" % (self.ressource, self.method))


class CheckRequest(Check):

    """
    Verifie la requete realisee sur divers criteres. La verification d'un critere
    est effectuee par l'appel de l'une des methodes definies ci-dessous.

    Les criteres attendus sont definis dans le fichier ressources.yml.
    """

    def __init__(self,query, ressources):
        self.ressources = ressources
        self.http_method = query.request_method
        self.method= query.method
        self.arguments = query.arguments
        self.ressource = query.ressource
        
    def __call__(self):
        try:
            if self.ressource not in self.ressources:
                raise RessourceNotFoundError(self.ressource)
            if self.method not in self.ressources[self.ressource]:
                raise MethodNotFoundError(self.method)
            if self.http_method != self.ressources[self.ressource][self.method]["request method"]:
                raise HTTPMethodError(
                    self.ressources[self.ressource][self.method]["request method"])
    
            expected_nb_arguments = len(
                self.ressources[self.ressource][self.method]["arguments"])
            received_nb_arguments = len(self.arguments)
    
            if expected_nb_arguments != received_nb_arguments:
                raise ArgumentError("Unexpected number of arguments: %i (expected %i)" % (
                    received_nb_arguments, expected_nb_arguments))
        except KeyError:
            raise ArgumentError("key not found in sources")


class CheckSource(Check):

    """
    Ensures source legitimacy according to sources.yml file
    """

    def __init__(self,query, sources,sha1check=True):
        self.sources = sources
        self.source = query.source
        self.ip = query.remote_ip
        self.signature = query.signature
        self.arguments = query.arguments
        self.sha1check = sha1check
       
    def __call__(self):
         
          try:
            if self.source not in self.sources:
                raise SourceNotFoundError("Unknown source %s" % self.source)
            # Check if IP is authorized
            if self.ip not in self.sources[self.source]["ip"]:
                raise IPNotAuthorizedError(self.ip)
            # Signature check
            if self.sha1check:
                arguments_list = sorted(self.arguments)
                to_hash = self.sources[self.source]["apikey"]
                for argument in arguments_list:
                    to_hash += (argument + self.arguments[argument])
                signkey = hashlib.sha1(to_hash.encode("utf-8")).hexdigest()
                if self.signature != signkey: 
                    raise WrongSignatureError(self.signature)
          except KeyError:
                raise SourceNotFoundError("key was not found in sources")
          except TypeError:
                raise SourceNotFoundError("key was not found in sources")

            
