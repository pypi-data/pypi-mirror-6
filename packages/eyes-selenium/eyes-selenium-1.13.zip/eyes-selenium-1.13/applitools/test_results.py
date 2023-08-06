class TestResults(object):
    """
    Eyes test results.
    """
    def __init__(self, steps=0, matches=0, mismatches=0, missing=0, exact_matches=0,
                 strict_matches=0, content_matches=0, layout_matches=0, none_matches=0):
        self.steps = steps
        self.matches = matches
        self.mismatches = mismatches
        self.missing = missing
        self.exact_matches = exact_matches
        self.strict_matches = strict_matches
        self.content_matches = content_matches
        self.layout_matches = layout_matches
        self.none_matches = none_matches

    def to_dict(self):
        return dict(steps=self.steps, matches=self.matches, mismatches=self.mismatches,
                    missing=self.missing, exact_matches=self.exact_matches,
                    strict_matches=self.strict_matches, content_matches=self.content_matches,
                    layout_matches=self.layout_matches, none_matches=self.none_matches)

    def __str__(self):
        return "[ steps: %d, matches: %d, mismatches: %d, missing: %d ]" % \
               (self.steps, self.matches, self.mismatches, self.missing)