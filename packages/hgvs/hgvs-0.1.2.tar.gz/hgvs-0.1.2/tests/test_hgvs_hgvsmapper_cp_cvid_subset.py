#
# c to p tests - cvid subset plus some additional tests (from Emily Hare)
#
import os
import unittest

import test_hgvs_hgvsmapper_cp_base

class TestHgvsCToPSubsetCvidsPlus(test_hgvs_hgvsmapper_cp_base.TestHgvsCToPBase):

    def test_hgvsc_to_hgvsp_cvid_subset_plus(self):
        infilename = 'cvid_subset_plus.tsv'
        outfilename = 'cvid_subset_plus.out'
        infile = os.path.join(os.path.dirname(__file__), 'data', infilename)
        outfile = os.path.join(os.path.dirname(__file__), 'data', outfilename)
        self._run_cp_test(infile, outfile)


if __name__ == '__main__':
    unittest.main()
## <LICENSE>
## Copyright 2014 HGVS Contributors (https://bitbucket.org/invitae/hgvs)
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##     http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## </LICENSE>
