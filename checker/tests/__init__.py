# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
from .result_test import *

# collection of upstream tests
from .upstream.test_check_upstream_sources import *
from .upstream.test_check_ufo_fontfamily_recommendations import *
from .upstream.test_check_ufo_requirements import *
from .upstream.test_check_ttx_fontfamily_recommendations import *
from .upstream.test_check_ttx_requirements import *
from .upstream.test_check_pyfontaine_subsets_coverage import *

# collection of downstream tests
from .metadata_test import *

from .downstream.test_description_404 import *
from .downstream.test_check_canonical_filenames import *
from .downstream.test_check_canonical_styles import *
from .downstream.test_check_canonical_weights import *
from .downstream.test_check_familyname_matches_fontnames import *
from .downstream.test_check_menu_subset_contains_proper_glyphs import *
from .downstream.test_check_metadata_matches_nametable import *
from .downstream.test_check_subsets_exists import *
from .downstream.test_check_unused_glyph_data import *
from .downstream.test_check_os2_width_class import *
from .downstream.test_check_no_problematic_formats import *
from .downstream.test_check_hmtx_hhea_max_advance_width_agreement import *
from .downstream.test_check_glyf_table_length import *
from .downstream.test_check_full_font_name_begins_with_family_name import *
from .downstream.test_check_upm_heights_less_120 import *
from .downstream.test_check_vertical_metrics import *
from .downstream.test_check_nbsp_width_matches_sp_width import *
from .downstream.test_check_font_sanitized_for_chrome_and_firefox import *
from .downstream.test_check_glyph_consistency import *
from .downstream.test_fontforge_validation_state import *
