import yaml
import re
import logging
import pkg_resources

from pywb.utils.dsrules import BaseRule, RuleSet

from pywb.utils.canonicalize import unsurt, UrlCanonicalizer

from query import CDXQuery


#=================================================================
def load_domain_specific_cdx_rules(ds_rules_file, surt_ordered):
    """
    >>> (canon, fuzzy) = load_domain_specific_cdx_rules(None, True)
    >>> canon('http://test.example.example/path/index.html?a=b&id=value&c=d')
    'example,example,test)/path/index.html?id=value'
    """
    canon = None
    fuzzy = None

    # Load Canonicalizer Rules
    rules = RuleSet(CDXDomainSpecificRule, 'canonicalize',
                    ds_rules_file=ds_rules_file)

    if not surt_ordered:
        for rule in rules:
            rule.unsurt()

    if rules:
        canon = CustomUrlCanonicalizer(rules, surt_ordered)

    # Load Fuzzy Lookup Rules
    rules = RuleSet(CDXDomainSpecificRule, 'fuzzy_lookup',
                    ds_rules_file=ds_rules_file)

    if not surt_ordered:
        for rule in rules:
            rule.unsurt()

    if rules:
        fuzzy = FuzzyQuery(rules)

    logging.debug('CustomCanonilizer? ' + str(bool(canon)))
    logging.debug('FuzzyMatcher? ' + str(bool(canon)))
    return (canon, fuzzy)


#=================================================================
class CustomUrlCanonicalizer(UrlCanonicalizer):
    def __init__(self, rules, surt_ordered=True):
        super(CustomUrlCanonicalizer, self).__init__(surt_ordered)
        self.rules = rules

    def __call__(self, url):
        urlkey = super(CustomUrlCanonicalizer, self).__call__(url)

        for rule in self.rules.iter_matching(urlkey):
            m = rule.regex.match(urlkey)
            if not m:
                continue

            if rule.replace:
                return m.expand(rule.replace)

        return urlkey


#=================================================================
class FuzzyQuery:
    def __init__(self, rules):
        self.rules = rules

    def __call__(self, query):
        matched_rule = None

        urlkey = query.key
        url = query.url
        filter_ = query.filters
        output = query.output

        for rule in self.rules.iter_matching(urlkey):
            m = rule.regex.search(urlkey)
            if not m:
                continue

            matched_rule = rule

            if len(m.groups()) == 1:
                filter_.append('~urlkey:' + m.group(1))

            break

        if not matched_rule:
            return None

        repl = '?'
        if matched_rule.replace:
            repl = matched_rule.replace

        inx = url.rfind(repl)
        if inx > 0:
            url = url[:inx + 1]

        params = {'url': url,
                  'matchType': 'prefix',
                  'filter': filter_,
                  'output': output}

        return CDXQuery(**params)


#=================================================================
class CDXDomainSpecificRule(BaseRule):
    def __init__(self, name, config):
        super(CDXDomainSpecificRule, self).__init__(name, config)

        if isinstance(config, basestring):
            self.regex = re.compile(config)
            self.replace = None
        else:
            self.regex = re.compile(config.get('match'))
            self.replace = config.get('replace')

    def unsurt(self):
        """
        urlkey is assumed to be in surt format by default
        In the case of non-surt format, this method is called
        to desurt any urls
        """
        self.url_prefix = map(unsurt, self.url_prefix)
        if self.regex:
            self.regex = unsurt(self.regex)

        if self.replace:
            self.replace = unsurt(self.replace)


if __name__ == "__main__":
        import doctest
        doctest.testmod()
