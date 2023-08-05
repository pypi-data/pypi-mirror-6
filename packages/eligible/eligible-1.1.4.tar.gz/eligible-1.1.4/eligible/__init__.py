#!/usr/bin/env python

api_base = 'https://gds.eligibleapi.com/v1.1'
api_key = None
api_version = '1.1'
test = False

import eligible.errors
from eligible.resources import (Acknowledgement,
                                Claim,
                                Coverage, 
                                Demographic,
                                Enrollment,
                                Medicare,
                                Payment,
                                Ticket,
                                X12)
