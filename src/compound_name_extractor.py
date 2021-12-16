"""
Script to find compound names from abstract text and derive list of compounds
ISSUES
* Leading "-"
* Missing base names
"""
import re
import nltk
from nltk.tokenize import WhitespaceTokenizer
# import miscellaneous_functions

tk = WhitespaceTokenizer()

# Regex for the main part of the name (e.g. (+)-4-oxo-3-chloro-compamaide)
NAME_BASE = "(\'|′|\"|\″|,|\+|\(|\)|\[|\]|\d|-|α|β|γ|δ|[A-Z]|[a-z]){4,200}"

# Regex for the characters that separate ranges (e.g. A - H)
# SEPARATORS = "[-~–−]"
SEPARATORS = "([-~–−]|to)"

# Regex for the terminus at the end of sentences or next to punctuation helps to find compounds with terminator suffixes
TERMINATORS = "[\s.,:;$\)]|$"

# Regex to describe compound suffixes (e.g. compoundine B12)
SUFFIX_TYPE_LIST = ["[A-Z]\d{0,2}", "[IVX]{1,5}"]

# List of allowed termini for compound names that are more than one word (e.g. allegic acid C)
TWO_WORD_NAME_TERMINI = ['acid', 'ester', 'acetate', 'butyrate', 'anhydride',
                         'methyl', 'ethyl', 'aglycon', 'aglycone', 'peroxide']

# Regex of possible variations on methyl ester
METHYL_ESTER_VARIATIONS = 'dimethyl ester|methyl ester|methyl ether'

# List of excluded names; Put diseases and other Excluded terms that are commonly matched in here:
EXCLUDED_NAMES = ["COMPOUND", "ALKALOID", "TERPENE", "POLYKETIDE", "MOIETY", "DEGREE", "STRUCTURE", "ANALOGUE",
                  "DERIVATIVE", "METABOLITE", "COENZYME", "TOPOISOMERASE", "COMPLEX", "DERIVATIVE", "REPORTED",
                  "AGAINST", "ALBICANS", "AERUGINOSA", "AUREUS", "COLI", "COMPONENT", "SYNTHASE", "COMPLEX",
                  "FACTOR", "WHEREA", "STIMULATION", "SYSTEM", "CYANOBACTERIA", "CANDIDUS", "ANALOG", "FRACTION",
                  "HEPATITIS", "HEPATITI", "EIGHTEEN", "CONGENER", "INHIBIT", "METHYL ESTER", "BENZOIC ACID",
                  'CONSTITUENT', 'INCLUDING', 'PRODUCT', 'DIFFRACTION', 'BROMINATED', 'CHLORINATED', 'ACTIVITY',
                  'ACCEPTOR', 'COMPLETE', 'CONSTITUENT', 'DECREASED', 'DEGENERATE', ' DERIVATE', ' DERIVATIVE',
                  'DERIVATES', 'PHENOLIC', 'EXPANSION', 'EXPERIMENTAL', 'ISOLATE', 'HYDRATE', 'PRODUCT', 'SCAFFOLD',
                  'VARIANT', 'THROUGH', 'STEREOISOMER', 'SUCCESSIVE', 'HOMOLOGUE', 'MULTIDIMENSIONAL', 'INVESTIGATING',
                  'EXPANSION', 'MONOESTER', 'SULFONE', 'SULFOXIDE', 'NITRILE', 'SKELETON', 'UNIFORMLY', 'HYDROLYZATE',
                  'METHANOATE', 'HEMIKETAL', 'EPOXYDON ESTER', 'ETHYL ACETATE', 'DIOXATRICYCLIC', 'CYCLOHEXENONE', 'KETONE',
                  'PROFILE', 'KINETICS', 'INVESTIGATE', 'HIGH-RESOLUTION', 'PROTOCOL', 'CONTENT', 'MATURITY', 'BETWEEN', 'ALCOHOL', 'TYPE', 'GROUP',
                  'SESQUITERPENE', 'GLYCOSIDE', 'SAPONIN', 'DIMER', 'ANTIBIOTIC']

EXCLUDED_PART_OF_NAMES = ['-TYPE', '-RELATED', '-INDUCED', '-TRIGGERED', '-RICH', '-LIKE', '-RESISTANT', '-BINDING', '-OXIDIZING', '-LINKED', '-BASED', '-DEGRADING',
                          '-CONVERTING', '-MEDIATED', '-PHASE', '-PRODUCING', 'SELECT', 'PURITY', 'SELECTIVITY', 'SELETIVE', '-UTILIZING', '-SUBSTITUTED', 
                          '-CONTAINING', '-DEPENDENT', '-FACING', '-DERIVED', '-PRODUCER', '-TREATED']

# List of natural product compound classes
COMPOUND_CLASS = ['ABEOLUPANE TRITERPENOID', 'ABEOTAXANE DITERPENOID', 'ABIETANE DITERPENOID', 'ACETONIDE', 'ACETOGENIN',
                  'ACRIDONE ALKALOID', 'ACYCLIC MONOTERPENOID', 'ACYCLIC TRITERPENOID', 'ACYL PHLOROGLUCINOL',
                  'AGAROFURAN SESQUITERPENOID', 'ALKALOID', 'AMARYLIDACEAE ALKALOID', 'AMIDE ALKALOID',
                  'AMINO ACID GLYCOSIDE', 'AMINO ACID', 'AMINO CYCLITOL', 'AMINO FATTY ACID', 'AMINOGLYCOSIDE',
                  'AMINOSUGAR', 'ANDROSTANE STEROID', 'ANGUCYCLINE', 'ANTHOCYANIDIN', 'ANTHRACYCLINE',
                  'ANTHRANILIC ACID ALKALOID', 'ANTHRANILLIC ACID DERIVATIVE', 'ANTHRAQUINONE', 'ANTHRONE',
                  'APOCAROTENOID', 'APORPHINE ALKALOID', 'APOTIRUCALLANE TRITERPENOID', 'ARBORINANE TRITERPENOID',
                  'AROMATIC POLYKETIDE', 'ARYLBENZOFURAN', 'ARYLNAPHTHALENE LIGNANS', 'ARYLTETRALIN LIGNAN',
                  'ATISANE DITERPENOID', 'AZAPHILONE', 'BACCHARANE TRITERPENOID', 'BACTOPRENOL',
                  'BAUERANE TRITERPENOID', 'BENZOFURAN', 'BENZENOID', 'BENZOPHENONE', 'BENZOPYRANONE', 'BENZOQUINONE',
                  'BERGAMOTANE SESQUITERPENOID', 'BEYERANE DITERPENOID', 'BIARYL TYPE DIARYLHEPTANOID',
                  'BISABOLANE SESQUITERPENOID', 'BISNAPHTHALENE', 'BRANCHED FATTY ACID',
                  'BRASILANE SESQUITERPENOID', 'BREVIANE DITERPENOID', 'BUFADIENOLIDE', 'BUTENOLIDE', 'BUTYROLACTONE',
                  'CADINANE SESQUITERPENOID', 'CAMPHANE MONOTERPENOID', 'CANNABINOID', 'CAPSAICINOID', 'CAPSAICIN',
                  'CARABRANE SESQUITERPENOID',
                  'CARBAZOLE ALKALOID', 'CARBOCYCLIC FATTY ACID', 'CARBOHYDRATE', 'CARBOLINE ALKALOID', 'CARDENOLIDE',
                  'CAROTENOID', 'CATECHOLAMINE', 'CATECHOL', 'CEMBRANE DITERPENOID', 'CEREBROSIDE', 'CERAMIDE',
                  'CHALCONE', 'CHEILANTHANE SESTERTERPENOID', 'CHOLANE STEROID', 'CHOLESTANE STEROID', 'CHROMANE',
                  'CHROMONE', 'CHROMAN'
                  'CINNAMIC ACID AMIDE', 'CINNAMOYL PHENOL', 'CLERODANE DITERPENOID', 'COLENSANE DITERPENOID',
                  'COPACAMPHANE SESQUITERPENOID', 'COUMARINOLIGNAN', 'COUMARIN', 'COUMARONOCHROMONE', 'COUMESTAN',
                  'CUBEBANE SESQUITERPENOID', 'CUCURBITANE TRITERPENOID', 'CYANOGENIC GLYCOSIDE', 'CYCLIC PEPTIDE',
                  'CYCLIC POLYKETIDE', 'CYCLITOL', 'CYCLOARTANE TRITERPENOID', 'CYCLOEUDESMANE SESQUITERPENOID',
                  'CYCLOPHYTANE DITERPENOID', 'CYTOCHALASAN ALKALOID', 'DAUCANE SESQUITERPENOID', 'DEPSIDE',
                  'DEPSIDONE', 'DEPSIPEPTIDE', 'DIACYLGLYCEROL', 'DIARYLHEPTANOID', 'DIAZOTETRONIC ACID',
                  'DIBENZOCYCLOOCTADIENES LIGNAN', 'DIBENZYLBUTANE LIGNAN', 'DIBENZYLBUTYROLACTONE LIGNAN',
                  'DICARBOXYLIC ACID', 'DIHYDROFLAVONOL', 'DIHYDROISOCOUMARIN', 'DIMERIC PHLOROGLUCINOL', 'DIPEPTIDE',
                  'DEPSIPEPTIDES', 'DIPHENYL ETHER',
                  'DISACCHARIDE', 'DITERPENE', 'DITERPENOID', 'DOCOSANOID', 'DRIMANE SESQUITERPENOID', 'ECDYSTEROID',
                  'EICOSANOID', 'ELEMANE SESQUITERPENOID', 'ENDOCANNABINOID', 'EREMOPHILANE SESQUITERPENOID',
                  'ERGOSTANE STEROID', 'ERICAMYCIN', 'ERYTHROMYCIN', 'EUDESMANE SESQUITERPENOID',
                  'EUPHANE TRITERPENOID', 'FARNESANE SESQUITERPENOID', 'FATTY ACID CONJUGATE', 'FATTY ACID',
                  'FATTY ACYL GLYCOSIDE', 'FATTY ACYL', 'FATTY ALCOHOL', 'FATTY ALDEHYDE', 'FATTY AMIDE',
                  'FATTY ESTER', 'FATTY NITRILE', 'FERNANE TRITERPENOID', 'FLAVAN-3-OL', 'FLAVANDIOL',
                  'LEUCOANTHOCYANIDIN', 'FLAVANONE', 'FLAVAN', 'FLAVONE', 'FLAVONOID', 'FLAVONOLIGNAN',
                  'FLAVONOL', 'FRIEDELANE TRITERPENOID', 'FURANOID LIGNAN', 'FUROCOUMARIN', 'FUROFURANOID LIGNAN',
                  'FUROSTANE STEROID', 'FUSIDANE TRITERPENOID', 'GALLOTANNIN', 'GAMMACERANE TRITERPENOID',
                  'GERANYLATED PHLOROGLUCINOL', 'GERMACRANE SESQUITERPENOID', 'GLUCOSINOLATE', 'GLUTINANE TRITERPENOID',
                  'GLYCEROLIPID', 'GLYCEROPHOSPHATE', 'GLYCEROPHOSPHOLIPID', 'GLYCOSIDES',
                  'GLYCOSYLMONOACYLGLYCEROL', 'GUAIANE SESQUITERPENOID', 'HALIMANE DITERPENOID',
                  'HALOGENATED HYDROCARBON', 'HASUBANAN ALKALOID', 'HETEROCYCLIC FATTY ACID', 'HISTIDINE ALKALOID',
                  'HOPANE TRITERPENOID', 'HYDROXY FATTY ACID', 'HYDROXY-HYDROPEROXYEICOSATETRAENOIC ACID',
                  'HYDROXY-HYDROPEROXYEICOSATRIENOIC ACID', 'ICETEXANE DITERPENOID', 'ILLUDALANE SESQUITERPENOID',
                  'ILLUDANE SESQUITERPENOID', 'IMIDAZOLE ALKALOID', 'INDOLE ALKALOID',
                  'INDOLE DIKETOPIPERAZINE ALKALOID', 'INDOLE-DITERPENOID ALKALOID', 'IRIDOID MONOTERPENOID',
                  'ISOBENZOFURANONE', 'ISOCHROMENONE', 'ISOCHROMAN',
                  'ISOCOUMARIN', 'ISOFLAVANONE', 'ISOFLAVONE', 'ISOFLAVONOID', 'ISOINDOLE ALKALOID',
                  'ISOPIMARANE DITERPENOID', 'ISOPROSTANE', 'ISOQUINOLINE ALKALOID', 'IVAXILLARANE SESQUITERPENOID',
                  'JASMONIC ACID', 'KAURANE DITERPENOID', 'KAVALACTONE', 'LABDANE DITERPENOID', 'LACTONE', 'LANOSTANE',
                  'LEUKOTRIENE', 'LIGNAN', 'LIMONOID', 'LIPOPEPTIDE', 'LIPOXIN', 'LONGIBORNANE SESQUITERPENOID',
                  'LUPANE TRITERPENOID', 'LYSINE ALKALOID', 'MACROLACTAMS', 'MACROLIDE LACTONE', 'MACROLIDE', 'MARESIN',
                  'MEGASTIGMANE',
                  'MENTHANE MONOTERPENOID', 'MEROHEMITERPENOID', 'MEROSESQUITERPENOID', 'MEROTERPENE', 'MEROTERPENOID',
                  'METHYL XANTHONE', 'MICROGININ', 'MINOR LIGNAN', 'MISCELLANEOUS POLYKETIDE', 'MONOACYLGLYCEROL',
                  'MONOCYCLIC MONOTERPENOID', 'MONOMERIC STILBENE', 'MONOSACCHARIDE', 'MONOTERPENE', 'MONOTERPENOID',
                  'MORETANE TRITERPENOID', 'MULTIFLORANE TRITERPENOID', 'MYRSINANE DITERPENOID', 'N-ACYL AMINE',
                  'N-ACYL ETHANOLAMINE', 'NAPHTHALENE', 'NAPHTHALENONE', 'NAPHTHOQUINONE', 'NEOFLAVONOID', 'NEOLIGNAN',
                  'NEUTRAL GLYCOSPHINGOLIPID', 'NICOTINIC ACID ALKALOID', 'NITRO FATTY ACID', 'NORKAURANE DITERPENOID',
                  'NORLABDANE DITERPENOID', 'NORTRITERPENOID', 'NUCLEOSIDE', 'OCTADECANOID', 'OLEANANE TRITERPENOID',
                  'OLIGOMERIC STIBENE',
                  'OLIGOPEPTIDE', 'ONOCERANE TRITERPENOID', 'OPEN-CHAIN POLYKETIDE', 'ORNITHINE ALKALOID',
                  'OTHER DOCOSANOID', 'OTHER OCTADECANOID', 'OXO FATTY ACID', 'OXYGENATED HYDROCARBON',
                  'PATCHOULANE SESQUITERPENOID', 'PERYLENEQUINONE', 'PEPTIDE ALKALOID', 'PERFORANE SESQUITERPENOID',
                  'PHENANTHRENE',
                  'PHENANTHRENOID', 'PHENOLIC ACID', 'PHENYLALANINE-DERIVED ALKALOID', 'PHENYLETHANOID',
                  'PHENYLETHYLAMINE', 'PHENYLPROPANOID', 'PHLOROGLUCINOL', 'PHTHALIDE', 'PHYLLOCLADANE DITERPENOID',
                  'PHYTANE DITERPENOID', 'PICROTOXANE SESQUITERPENOID', 'PIMARANE DITERPENOID', 'PINANE MONOTERPENOID',
                  'PINGUISANE SESQUITERPENOID', 'PIPERIDINE ALKALOID', 'PODOCARPANE DITERPENOID', 'POLYAMINE',
                  'POLYCYCLIC AROMATIC POLYKETIDE', 'POLYENE MACROLIDE', 'POLYKETIDE', 'POLYOL', 'POLYPRENOL',
                  'POLYPRENYLATED CYCLIC POLYKETIDE', 'POLYSACCHARIDE', 'PREGNANE STEROID',
                  'PRENYL QUINONE MEROTERPENOID', 'PROANTHOCYANIN', 'PROSTAGLANDIN', 'PROTOBERBERINE ALKALOID',
                  'PROTOPINE ALKALOID', 'PSEUDOALKALOID', 'PSEUDOGUAIANE SESQUITERPENOID', 'PSEUDOPTERANE DITERPENOID',
                  'PTEROCARPAN', 'PULVINONE', 'PURINE ALKALOID', 'PYRANOCOUMARIN', 'PYRANONAPHTHOQUINONE',
                  'PYRIDINE ALKALOID', 'NAPHTHOPYRONE', 'PYRONE',
                  'PYRROLIDINE ALKALOID', 'QUASSINOID', 'QUINOLINE ALKALOID', 'QUINONE', 'ROTENOID', 'SACCHARIDE',
                  'SCALARANE SESTERTERPENOID', 'SECOABIETANE DITERPENOID', 'SECOIRIDOID MONOTERPENOID',
                  'SECOKAURANE DITERPENOID', 'SERRATANE TRITERPENOID', 'SESQUITERPENE', 'SESQUITERPENOID',
                  'SESTERTERPENOID',
                  'SHIKIMATE', 'SIDEROPHORE', 'SMALL PEPTIDE', 'SOLANAPYRONE', 'SPHINGOID BASE',
                  'SPHINGOLIPID',
                  'SPIROSTANE STEROID', 'SPONGIANE DITERPENOID', 'SPRIROMEROTERPENOID', 'STEROIDAL ALKALOID',
                  'STEROID', 'STIGMASTANE STEROID', 'STILBENOID', 'STILBENOLIGNAN', 'STYRYLPYRONE',
                  'TARAXASTANE TRITERPENOID', 'TARAXERANE TRITERPENOID', 'TAXANE DITERPENOID', 'TERPENE ALKALOID',
                  'TERPENE', 'TERPENOID ALKALOID', 'TERPENOID', 'TERPHENYL', 'TERREULACTONE', 'TETRACYCLIC DITERPENOID',
                  'TETRAHYDROISOQUINOLINE ALKALOID', 'TETRAKETIDE MEROTERPENOID', 'TETRONATE', 'THIA FATTY ACID',
                  'TIRUCALLANE TRITERPENOID', 'TOTARANE DITERPENOID', 'TRACHYLOBANE DITERPENOID', 'TRIACYLGLYCEROL',
                  'TRIKETIDE MEROTERPENOID', 'TRIPEPTIDE', 'TRITERPENE', 'TRITERPENOID', 'TROPOLONE',
                  'TRYPTOPHAN ALKALOID', 'TYROSINE ALKALOID', 'UNSATURATED FATTY ACID', 'URSANE TRITERPENOID',
                  'USNIC ACID AND DERIVATIVE', 'VALERANE SESQUITERPENOID', 'WAX MONOESTER', 'XANTHONE', 'ZEARALENONE',
                  'ABEOABIETANE DITERPENOID', 'NAPHTHO-Γ-PYRONE', 'PHENYLSPIRODRIMANE', 'LIPOPEPTIDE', 'MACROLIDE',
                  'SORBICILLINOID', 'GLUCOSIDE', 'CHAMIGRANE', 'CYTOCHALASANE', 'ERGOSTANE', 'PEPTIDE',
                  'ALKYLRESORSINOL', 'FLUORENE', 'GUANIDINE ALKALOID', 'LINEAR POLYKETIDE', 'MITOMYCIN DERIVATIVE',
                  'MYCOSPORINE DERIVATIVE', 'POLYETHER', 'PROLINE ALKALOID', 'SERINE ALKALOID', 'TETRAMATE ALKALOID',
                  'Β-LACTAM', 'Γ-LACTAM-Β-LACTONE', 'INDOLOCARBAZOLE', 'HYDROXYANTHRAQUINONE', 'HEPTAPEPTIDE',
                  'FURANONE', 'DIPHENYLETHER', 'DIKETOPIPERAZINE', 'DIHYDROXANTHONE', 'DIHYDROBENZOFURAN', 'XANTHENE',
                  'DIHYDROCHROMONE DIMER', 'YANUTHONE', 'MACROLACTAM', 'GIBBERELLINS', 'MYCOTOXIN', 'POLYKETIDE',
                  'γ-Lactam', 'γ-Lactone', 'MACROLACTIN', 'PHYTOTOXIN', 'SECONDARY METABOLITE', 'SPIRODITERPENOIDS', 'STEROL',
                  'SERINE', 'GLYCOSIDE', 'BENZAMIDE', 'ISOINDOLIN-1-ONE', 'PHTHALIMIDINE', 'INDOLE-DITERPENOID', 'RIBOSE',
                  'PHENYLCYCLOPENTENONE', 'CYTOCHALASIN', 'PHENAZINE', 'EPOTHILONE', 'GUAIANE', 'GANODERIC ACID', 'NOCAPYRONE', 
                  'HYDROQUINONE', 'DIORCINOL', 'SULFONOLIPID', 'ERGOSTEROL', 'GUANINE', 'PLAKINAMINE', 'HEXAHYDROANTHRAQUIONE',
                  'α-FURANONE', 'NAPHTHYLISOQUINOLINE', 'URIDINE', 'α-IONONE', 'SAPONIN', 'GALLIC ACID', 'QUINOLONE',
                  'DIGLYCOSIDE', 'LACTATE', 'MEROTERPENOID', 'ABIETANE']

def bracket_matched(string):
    """ Function to check if brackets are matched; For every open bracket, there should be a matching closed bracket.
                    :param string: string to be checked
                    :return: count if == 0, else returns false"""
    count = 0
    for i in string:
        if i in ["(", "[", "{", "<"]:
            count += 1
        elif i in [")", "]", "}", ">"]:
            count -= 1
        if count < 0:
            return False
    return count == 0


# Python3 program to remove invalid parenthesis using modified code from: https://www.geeksforgeeks.org/remove-invalid-parentheses/
def is_parentheses(c):
    """ Method checks if character is parenthesis(open or closed)
            :param c: character
            :return: if it is open/closed parentheses
            """
    return (c == '(') or (c == ')')


def remove_invalid_parentheses(string):
    """ Method to remove invalid parenthesis
                    :param string: string
                    :return: False if open bracket otherwise 0 when valid parentheses
                    """
    if len(string) == 0:
        return

    # visit set to ignore already visited
    visit = set()

    # queue to maintain BFS
    q = []
    temp = 0
    level = 0

    # pushing given as starting node into queue
    q.append(string)
    visit.add(string)
    while len(q):
        string = q[0]
        q.pop()

        if bracket_matched(string):
            level = True  # If answer is found, make level true; so that valid of only that level are processes
            return string

        if level:
            continue
        for i in range(len(string)):
            if not is_parentheses(string[i]):
                continue

            # Removing parenthesis from str and pushing into queue,if not visited already
            temp = string[0:i] + string[i + 1:]
            if temp not in visit:
                q.append(temp)
                visit.add(temp)


def name_search(text):
    def names_letter_range_add(compound_names_list, match, root_name_variable, suffix_start_point, suffix_end_point,
                               match_index, texts):
        """ Function for appending chemical compound names to list of compound names detected within the abstract text.
                :param compound_names_list: list of all compound names found in abstract text
                :param root_name_variable: root of the chemical name
                :param suffix_start_point: starting point location of suffix
                :param suffix_end_point: ending point location of suffix
                :param match_index: match index location
                :param texts: abstract text
                :return: none"""
        try:
            temp_compound_names_list = []
            match_escaped = re.escape(match[0])
            comp_range_check = re.findall(r"%s(?:\s)?(?:\()?\d+(?:\s)?\-(?:\s)?\d+(?:\s)?(?:\))?" % match_escaped, texts)
            # print("comp_range_check ", comp_range_check)

            if comp_range_check:
                comp_range_count = 0
                number_range = re.findall(r"\d+", comp_range_check[0])

                # print("number_range: ", number_range)
                if len(number_range) == 2:
                    for i in range(int(number_range[0]), int(number_range[1])+1):
                        comp_range_count = comp_range_count + 1
                # print(comp_range_count)

                for char in range(ord(suffix_start_point), ord(suffix_end_point) + 1):
                    chem_name = root_name_variable[0].upper() + root_name_variable[1:] + chr(char)
                    # if chem_name not in compound_names_list:
                    temp_compound_names_list.append((chem_name, match_index, texts))
                
                # print("alpha: ", comp_range_count, len(temp_compound_names_list))
                if comp_range_count == 0 or comp_range_count == len(temp_compound_names_list):
                    for chem in temp_compound_names_list:
                        if chem[0] in compound_names_list:
                            temp_compound_names_list.remove(chem)
                    for chem in temp_compound_names_list:
                        compound_names_list.append(chem)

            else:
                for char in range(ord(suffix_start_point), ord(suffix_end_point) + 1):
                    chem_name = root_name_variable[0].upper() + root_name_variable[1:] + chr(char)
                    if chem_name not in compound_names_list:
                        compound_names_list.append((chem_name, match_index, texts))

        except AttributeError as e1:
            print(e1)
        except ValueError as e2:
            print(e2)
        except KeyError as e3:
            print(e3)

    def names_roman_numeral_range_add(compound_names_list, match, root_name_variable, suffix_start_point, suffix_end_point,
                                      match_index, texts):
        """ Function for appending chemical compound names to list of compound names detected within the abstract text.
                :param compound_names_list: list of all compound names found in abstract text
                :param root_name_variable: root of the chemical name
                :param suffix_start_point: starting point location of suffix
                :param suffix_end_point: ending point location of suffix
                :param match_index: match index location
                :param texts: abstract text
                :return: none"""
        numeral_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
                          "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18,
                          "XIX": 19, "XX": 20, "XXI": 21, "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25, "XXVI": 26, 
                          "XXVII": 27, "XXVIII": 28, "XXIX": 29, "XXX": 30, "XXXI": 31, "XXXII": 32, "XXXIII": 33,
                          "XXXIV": 34, "XXXV": 35, "XXXVI": 36, "XXXVII": 37, "XXXVIII": 38, "XXXIX": 39, "XXXX": 40}
        int_to_numeral = {v: k for k, v in numeral_to_int.items()}
        try:
            temp_compound_names_list = []
            match_escaped = re.escape(match[0])
            comp_range_check = re.findall(r"%s(?:\s)?\d+(?:\s)?\-(?:\s)?\d+(?:\s)?" % match_escaped, texts)
            # print("comp_range_check ", comp_range_check)

            if comp_range_check:
                comp_range_count = 0
                number_range = re.findall(r"\d+", comp_range_check[0])

                # print("number_range: ", number_range)
                if len(number_range) == 2:
                    for i in range(int(number_range[0]), int(number_range[1])+1):
                        comp_range_count = comp_range_count + 1
                # print(comp_range_count)

                for char in range(numeral_to_int[suffix_start_point], numeral_to_int[suffix_end_point] + 1):
                    chem_name = root_name_variable.capitalize() + " " + int_to_numeral[char]
                    temp_compound_names_list.append((chem_name, match_index, texts))
                
                # print("roman: ", comp_range_count, len(temp_compound_names_list))
                if comp_range_count == 0 or comp_range_count == len(temp_compound_names_list):
                    for chem in temp_compound_names_list:
                        if chem[0] in compound_names_list:
                            temp_compound_names_list.remove(chem)

                    for chem in temp_compound_names_list:
                        compound_names_list.append(chem)
            else:
                for char in range(numeral_to_int[suffix_start_point], numeral_to_int[suffix_end_point] + 1):
                    chem_name = root_name_variable.capitalize() + " " + int_to_numeral[char]
                    if chem_name not in compound_names_list:
                        compound_names_list.append((chem_name, match_index, texts))


        except AttributeError as e1:
            print(e1)
        except ValueError as e2:
            print(e2)
        except KeyError as e3:
            print(e3)

    def name_add(compound_names_list, chem_name, match_index, texts):
        """ Function for appending a chemical compound name to the list of compound names detected within the abstract text.
                        :param compound_names_list: list of all compound names found in abstract text
                        :param chem_name: detected chemical compound name
                        :param match_index: match index location
                        :param texts: abstract text
                        :return: none"""
        # Check name has sensible brackets
        if bracket_matched(chem_name):
        # if miscellaneous_functions.bracket_matched(chem_name):
            # Check name isn't already in the list
            if chem_name.lower() not in [n[0].lower() for n in compound_names_list]:
                compound_names_list.append((chem_name, match_index, texts))
    

    def group_listed_comps(abstract_text, comp_name_list, base_names_list, separators_list, terminators_list,
                           two_word_termini_list, excluded_names_list):
        """ Look for compound names listed in groups (e.g. Examplamides A - C), appends compound names to the list
        of all compound names found in the abstract text
                :param abstract_text: raw string of abstract text
                :param comp_name_list: list of all compound names found in abstract text
                :param base_names_list: regex for the main part of the name (e.g. (+)-4-oxo-3-chloro-compamaide)
                :param separators_list:  regex for the characters that separate ranges (e.g. A - H)
                :param terminators_list: regex for the terminus if the search. helps to find compounds with suffixes
                that are at the end of sentences or next to punctuation.
                :param two_word_termini_list: list of allowed termini for compound names that are more than one word
                (e.g. allegic acid C)
                :param excluded_names_list: list of excluded names
                :return: none
                """
        # match_count = 0

        search_matches = re.finditer(
            '((' + base_names_list + ')\s)?(' + base_names_list + ')[\s-]([A-Z]{1,2}(?:\d{1,2})?)\s?' + separators_list + '\s?([A-Z]{1,2}(?:\d{1,2})?)(' + terminators_list + ')',
            abstract_text)

        if search_matches:
        # if match_count > 0:
            for match in search_matches:
                # print("group_listed_comps: ", match)
                findall_list = tuple(match.groups())
                actual_match_span = match.span()
                # print("group_findall_list ", findall_list)
                            
                if isinstance(findall_list, tuple):
                        # print("entry: ", entry)
                    try:
                        if len(findall_list[3]) > 0:
                            root_name = findall_list[3].rstrip('s')
                            # print("root_name: ", root_name)
                            if root_name in two_word_termini_list:
                                root_name = findall_list[1].rstrip() + " " + root_name
                            else:
                                actual_match = re.finditer('(' + base_names_list + ')[\s-]([A-Z]{1,2}(?:\d{1,2})?)\s?' + separators_list + '\s?([A-Z]{1,2}(?:\d{1,2})?)(' + terminators_list + ')',abstract_text)
                                for i in actual_match:
                                    actual_match_span = i.span()

                            # Removes matches with very short words such as "among them, III and IV" that are not real compounds.
                            # if len(root_name) < 7:
                            #     continue
                            # elif root_name in excluded_names_list:
                            #     continue

                            if len(root_name) > 6 and root_name not in excluded_names_list:
                            
                            # else: 
                                suffix_start = findall_list[5]
                                if not re.match(r"[A-Z]{1,2}", findall_list[6]):
                                    suffix_end = findall_list[7]
                                else:
                                    suffix_end = findall_list[6]
                                # print(suffix_start, suffix_end)

                                temp_root_name = ""
                                
                                if re.match(r"^[A-Z]{1,2}\d{1,2}$", suffix_start) and re.match(r"^[A-Z]{1,2}\d{1,2}$", suffix_end):

                                    if len(suffix_start) == len(suffix_end):
                                        range_len = len(suffix_start)

                                        temp_root_name = root_name.capitalize() + " "
                                        
                                        for i in range(0, range_len):
                                            # print("i: ", i, suffix_start[i], suffix_end[i])
                                            if suffix_start[i].isalpha():
                                                if suffix_start[i] != suffix_end[i]:
                                                    break
                                                else:
                                                    temp_root_name = temp_root_name + suffix_start[i]
                                                    # print("temp_root_name isalpha(): ", temp_root_name)

                                            elif suffix_start[i].isdigit():
                                                if ord(suffix_start[i]) > ord(suffix_end[i]):
                                                    break
                                                elif suffix_start[i] == suffix_end[i]:
                                                    temp_root_name = temp_root_name + str(suffix_start[i])
                                                    # print("elif ", temp_root_name)
                                                else:
                                                    # print("temp_root_name ", temp_root_name)
                                                    comp_range_check = tk.tokenize(abstract_text[actual_match_span[1]:])
                                                    # print(comp_range_check)
                                                    names_letter_range_add(comp_name_list, match, temp_root_name, suffix_start[i], suffix_end[i], actual_match_span, abstract_text)

                                elif re.match(r"^[A-Z]{1}$", suffix_start) and re.match(r"^[A-Z]{1}$", suffix_end):
                                    
                                    temp_root_name = root_name.capitalize() + " "
                                    # print("in else: ", root_name)

                                # print(comp_name_list, root_name, suffix_start, suffix_end, match.span())
                                    names_letter_range_add(comp_name_list, match, temp_root_name, suffix_start, suffix_end, actual_match_span,
                                                        abstract_text)
                        
                    except AttributeError as error:
                        print(error)
                    except ValueError as error:
                        print(error)
                    except TypeError as error:
                        print(error)


    def explict_suffix_listed_comps(abstract_text, comp_name_list, name_base_list, suffix_type_list,
                                    two_word_termini_list, excluded_names_list):
        """ look for compounds where suffixes are listed explicitly (e.g. Examplamides A, B and C). This search
        accounts for situations where compound numbers are also included (e.g. Examplamides A (1), B (2) and C (3)).
        It also handles both single letters, letters followed by one or two digits, and Roman numerals.
                        :param abstract_text: raw string of abstract text
                        :param comp_name_list: list of all compound names found in abstract text
                        :param name_base_list: regex for the main part of the name (e.g. (+)-4-oxo-3-chloro-compamaide)
                        :param suffix_type_list:  regex for the characters that separate ranges (e.g. A - H)
                        :param two_word_termini_list: list of allowed termini for compound names that are more
                        than one word (e.g. allegic acid C)
                        :param excluded_names_list: list of excluded names
                        :return: none
                        """
        for suffix_type in suffix_type_list:
            search_match = re.finditer(
                '((' + name_base_list + ')\s)?(' + name_base_list + ')[\s|-](' + suffix_type + ')(\s\(\d{1,2}\))?(([,][\s]' + suffix_type +
                '(\s\(\d{1,2}\))?){0,20}),?\s(and)\s(' + suffix_type + ')', abstract_text)
            if search_match:
                for match in search_match:
                    # print("explict_suffix_listed_comps: ", match)
                    findall_list = tuple(match.groups())
                    if isinstance(findall_list, tuple):

                        for entry in findall_list:
                            try:
                                root_name = findall_list[3].rstrip('s')
                                if root_name in two_word_termini_list:
                                    # print(root_name)
                                    root_name = findall_list[1].rstrip().rstrip('s') + " " + root_name
                                # Removes matches with very short words such as "among them, III and IV" that are not real compounds.
                                if len(root_name) < 7:
                                    continue
                                elif root_name.upper() in excluded_names_list:
                                    continue
                                else:
                                    suffix_list = (findall_list[7]).split(", ")[1:]
                                    suffix_list.append(findall_list[5])
                                    suffix_list.append(findall_list[11])
                                    for suffix in suffix_list:
                                        # This is required to remove the bracketed numbers if these are
                                        # in the original text (e.g. Wawawa A (1), B (2), C (3) and D (4))
                                        if re.search("[\(]", suffix):
                                            suffix = suffix.split("(")[0].rstrip()
                                        name = root_name.capitalize() + " " + suffix
                                        name_add(comp_name_list, name, match.span(), abstract_text)
                                        
                            except AttributeError as error:
                                print(error)
                            except ValueError as error:
                                print(error)
                            except TypeError as error:
                                print(error)

    def methyl_ester_finder(abstract_text, comp_name_list, methyl_ester_finder_list):
        """For the detection of certain cases of methyl esters or similar types, such as dimethyl ether or methyl ester.
                                :param abstract_text: raw string of abstract text
                                :param comp_name_list: list of all compound names found in abstract text
                                :param methyl_ester_finder_list: regex pattern for different types of esters of ethers
                                :return: none
                                """
        # Capture two segments of text that doesn't include whitespace characters (a word) prior to "methyl ester"
        # 1. Ex. "Helvolic acid methyl ester (1)" or "Ochratoxin A methyl ester (2)"
        ce = re.finditer('(\S+)\s(acid|[A-Z])\s(' + methyl_ester_finder_list + ')\s+(\(\d\))', abstract_text)
        
        try:
            if ce:
                for match in ce:
                    findall_list = tuple(match.groups())
                    for entry in findall_list:
                        comp_name = '{0} {1} {2}'.format(findall_list[0].rstrip().capitalize(), findall_list[1].rstrip(),
                                                        findall_list[2].rstrip())
                        name_add(comp_name_list, comp_name, match.span(), abstract_text)

            # 2. Or 3 words: Ex. "6′,6-cryptoporic acid G dimethyl ester (1)"
            ce_double = re.finditer('(\S+)\s(acid|[A-Z])\s(acid|[A-Z])\s(' + methyl_ester_finder_list + ')\s+(\(\d\))',
                                    abstract_text)
            if ce_double:
                for match in ce_double:
                    findall_list = tuple(match.groups())  # Convert iterable object into
                    for entry in findall_list:
                        comp_name = '{0} {1} {2} {3}'.format(findall_list[0].rstrip().capitalize(),
                                                            findall_list[1].rstrip(), findall_list[2].rstrip(),
                                                            findall_list[3].rstrip())
                        name_add(comp_name_list, comp_name, match.span(), abstract_text)

            # 3. Or just 1 word like Secoxyloganin methyl ester (1)
            ce_single = re.finditer('(\S+[^A-Z]^acid)\s(' + methyl_ester_finder_list + ')\s+(\(\d\))', abstract_text)
            if ce_single:
                for match in ce_single:
                    findall_list = tuple(match.groups())
                    for entry in findall_list:
                        comp_name = '{0} {1}'.format(findall_list[0].rstrip().capitalize(), findall_list[1].rstrip())
                        name_add(comp_name_list, comp_name, match.span(), abstract_text)

            # Benzoic acid finder
            ce_single2 = re.finditer('(\S+)\s(benzoic acid)\s+(\(\d\))', abstract_text)
            if ce_single2:
                for match in ce_single2:
                    findall_list = tuple(match.groups())
                    for entry in findall_list:
                        comp_name = '{0} {1}'.format(findall_list[0].rstrip().capitalize(), findall_list[1].rstrip())
                        name_add(comp_name_list, comp_name, match.span(), abstract_text)

            # Captures a word prior to "methyl ester" that could have any text that doesn't include whitespace characters with it
            # Like alternariol 1'-hydroxy-9-methyl ether (1)
            se = re.finditer('(\S+[^A-Z])\s(\S+)(' + methyl_ester_finder_list + ')\s+(\(\d\))', abstract_text)
            if se:
                for match in se:
                    findall_list = tuple(match.groups())
                    for entry in findall_list:
                        comp_name = '{0} {1}{2}'.format(findall_list[0].rstrip().capitalize(), findall_list[1].rstrip(),
                                                        findall_list[2].rstrip())
                        name_add(comp_name_list, comp_name, match.span(), abstract_text)
        
        except AttributeError as error:
            print(error)
        except ValueError as error:
            print(error)
        except TypeError as error:
            print(error)

    def post_comps_numbers(abstract_text, comp_name_list, name_base_list, suffix_type_list, two_word_termini_list,
                           excluded_names_list, separators_list, range_comp_list):
        """ Look for compounds that are followed by a compound number (e.g. (1)) or range of numbers (e.g. (1 - 3))
                        :param abstract_text: raw string of abstract text
                        :param comp_name_list: list of all compound names found in abstract text
                        :param name_base_list: regex for the main part of the name (e.g. (+)-4-oxo-3-chloro-compamaide)
                        :param suffix_type_list:  regex for the characters that separate ranges (e.g. A - H)
                        :param two_word_termini_list: list of allowed termini for compound names that are more
                         than one word (e.g. allegic acid C)
                        :param excluded_names_list: list of excluded names
                        :param separators_list: regex for the characters that separate ranges (e.g. A - H)
                        :return: none
                        """
        for suffix_type in suffix_type_list:
            c = re.finditer(
                '(' + name_base_list + '\s)?(' + name_base_list + ')\s((' + suffix_type + ')\s)?(\(\d{1,2}(\s?' + separators_list + '\s?\d{1,2})?\))',
                abstract_text)
            if c:
                for match in c:
                    # print("post_comps_numbers: ", match) 

                    findall_list = tuple(match.groups())
                    # print("findall_list ", findall_list)

                    if isinstance(findall_list, tuple):
                        # for entry in findall_list:
                        try:
                            if findall_list[2] in two_word_termini_list:
                                root_name = findall_list[0].rstrip().rstrip('s') + " " + findall_list[2].rstrip().rstrip('s')
                                if root_name[0].isalpha():
                                    root_name = root_name[0].upper() + root_name[1:]
                            # this requirement removes short 'words' like (1)H, and (4), that otherwise get selected as hits.
                            elif len(findall_list[2]) < 8 and re.search("[\'′\",+\(\)]", findall_list[2]):
                                continue
                            else:
                                root_name = findall_list[2].rstrip().rstrip('s')
                                if root_name[0].isalpha():
                                    root_name = root_name[0].upper() + root_name[1:]
                                # print(root_name)

                            if root_name.upper() in excluded_names_list:
                                continue
                            if len(root_name) < 7:
                                continue

                            if findall_list[5]:
                                name = root_name + " " + findall_list[5]
                                left_bracket = re.findall("\(", name)
                                right_bracket = re.findall("\)", name)
                                if len(left_bracket) == 1 and len(right_bracket) == 1:        
                                    if name[0] == "(" and name[len(name)-1] == ")":
                                        name = name.strip("(")
                                        name = name.strip(")")
                                        name = name[0].upper() + name[1:]
                            else:
                                name = root_name
                                left_bracket = re.findall("\(", name)
                                right_bracket = re.findall("\)", name)
                                if len(left_bracket) == 1 and len(right_bracket) == 1:        
                                    if name[0] == "(" and name[len(name)-1] == ")":
                                        name = name.strip("(")
                                        name = name.strip(")")
                                        name = name[0].upper() + name[1:]
                            
                            for comp in range_comp_list:
                                if comp[1][0] >= match.start() and comp[1][1] <= match.end():
                                    # print("comp[1][0] ", comp[1][0])
                                    break
                            else:
                                actual_match_split = re.split("\s", match[0])
                                # print("split: ", actual_match_split)
                                acutal_match = ""
                                acutal_match_start = 0

                                if len(actual_match_split) > 0:
                                    for term in actual_match_split:
                                        if term.lower() in name.lower():
                                            acutal_match = term
                                            break
                                    
                                    # print("acutal_match: ", acutal_match)
                                    acutal_match = re.escape(acutal_match)
                                    actual_match_list = re.finditer(r"%s" % acutal_match, match[0])
                                    for i in actual_match_list:
                                        # print("actual_match: ", i)
                                        acutal_match_start = match.start() + i.start()
                                        # print("new_match: ", i.start(), "original_match_len: ", original_match_len, "acutal_match_start: ", acutal_match_start, "new_start:", match.start() + acutal_match_start)
                                        name_add(comp_name_list, name, (acutal_match_start, match.end()), abstract_text)
                                else:
                                    name_add(comp_name_list, name, match.span(), abstract_text)
                            
                        except AttributeError as error:
                            print(error)
                        except ValueError as error:
                            print(error)
                        except TypeError as error:
                            print(error)

    def roman_numeral_suffix_comps(abstract_text, comp_name_list, name_base_list, two_word_termini_list,
                                   excluded_names_list, separators_list, terminators_list):
        """ Look for compounds that have Roman numeral suffixes listed in groups (e.g. Examplamides III - IX)
                    :param abstract_text: raw string of abstract text
                    :param comp_name_list: list of all compound names found in abstract text
                    :param name_base_list: regex for the main part of the name (e.g. (+)-4-oxo-3-chloro-compamaide)
                    :param terminators_list: regex for the terminus if the search. Helps to find compounds with suffixes
                    that are at the end of sentences or next to punctuation.
                    :param two_word_termini_list: list of allowed termini for compound names that are more than one word
                     (e.g. allegic acid C)
                    :param excluded_names_list: list of excluded names
                    :param separators_list: regex for the characters that separate ranges (e.g. A - H)
                    :return: none
                        """
        d = re.finditer(
            '(' + name_base_list + '\s)?(' + name_base_list + ')[\s-]([IVX]{1,5})\s?' + separators_list + '\s?([IVX]{1,5})(' + terminators_list + ')',
            abstract_text)
        if d:
            for match in d:
                # print("roman_numeral_suffix_comps: ", match)
                findall_list = tuple(match.groups())
                # print("findall_list: ", findall_list)
                if isinstance(findall_list, tuple):
                    # for entry in findall_list:
                    try:
                        root_name = findall_list[2].rstrip('s')
                        if root_name in two_word_termini_list:
                            root_name = findall_list[0].rstrip() + " " + root_name

                        if len(root_name) > 6 and root_name.upper() not in excluded_names_list:
                        # else:
                            
                            suffix_start = findall_list[4]
                            suffix_end = findall_list[6]
                            # print(suffix_start, suffix_end)
                            names_roman_numeral_range_add(comp_name_list, match, root_name, suffix_start, suffix_end, match.span(),
                                                        abstract_text)
                    except AttributeError as error:
                        print(error)
                    except ValueError as error:
                        print(error)
                    except TypeError as error:
                        print(error)

    def single_comps(abstract_text, comp_name_list, name_base_list, suffix_type_list, two_word_termini_list,
                     excluded_names_list, terminators_list):
        """ Look for compounds that are followed by a compound number (e.g. (1)) or range of numbers (e.g. (1 - 3))
                            :param abstract_text: raw string of abstract text
                            :param comp_name_list: list of all compound names found in abstract text
                            :param name_base_list: regex for the main part of the name (e.g. (+)-4-oxo-3-chloro-compamaide)
                            :param terminators_list: regex for the terminus if the search. Helps to find compounds with suffixes
                            that are at the end of sentences or next to punctuation.
                            :param two_word_termini_list: list of allowed termini for compound names that are more than one word
                             (e.g. allegic acid C)
                            :param excluded_names_list: list of excluded names
                            :param suffix_type_list:  regex for the characters that separate ranges (e.g. A - H)
                            :return: none
                                """
        # look for instances of single compounds (single letters, letters followed by one or two digits, and Roman numerals)
        for suffix_type in suffix_type_list:
            e = re.finditer(
                '(' + name_base_list + '\s)?(' + name_base_list + ')\s(' + suffix_type + ')(' + terminators_list + ')',
                abstract_text)

            if e:
                for match in e:
                    findall_list = tuple(match.groups())

                    if isinstance(findall_list, tuple):
                        for entry in findall_list:
                            try:
                                if findall_list[2] in two_word_termini_list:
                                        name = findall_list[0].rstrip().rstrip('s').capitalize() + " " + findall_list[2] + " " + \
                                            findall_list[4]
                                # Removes matches with very short words such as "among them, III and IV" that are not real compounds.
                                elif len(findall_list[2]) < 7:
                                    continue
                                elif findall_list[2].rstrip().rstrip('s').upper() in excluded_names_list:
                                    continue
                                else:
                                    name = findall_list[2].rstrip().rstrip('s').capitalize() + " " + findall_list[4]

                                name_add(comp_name_list, name, match.span(), abstract_text)


                                # Add just the word closest to the bracket (e.g. lodophilone from "alkaloid lodophilone (1)"
                                # Only do this if the second word is longer than 5 characters and isn't both short and containing special characters
                                if len(findall_list[1]) > 4 and not (
                                        len(findall_list[1]) < 8 and re.search("[\'′\",+\(\)]", findall_list[1])):
                                    if findall_list[1].rstrip().rstrip('s').upper() in excluded_names_list:
                                        continue
                                else:
                                    name = findall_list[1].rstrip().rstrip('s').capitalize() + " " + findall_list[2]
                                    name_add(comp_name_list, name, match.span(), abstract_text)

                            except AttributeError as error:
                                print(error)
                            except ValueError as error:
                                print(error)
                            except TypeError as error:
                                print(error)


    compound_names = []  # list of chemical name
    range_compound_names = []

    group_listed_comps(text, range_compound_names, NAME_BASE, SEPARATORS, TERMINATORS, TWO_WORD_NAME_TERMINI, EXCLUDED_NAMES)
    roman_numeral_suffix_comps(text, range_compound_names, NAME_BASE, TWO_WORD_NAME_TERMINI, EXCLUDED_NAMES, SEPARATORS, TERMINATORS)
    explict_suffix_listed_comps(text, compound_names, NAME_BASE, SUFFIX_TYPE_LIST, TWO_WORD_NAME_TERMINI,
                                EXCLUDED_NAMES)
    methyl_ester_finder(text, compound_names, METHYL_ESTER_VARIATIONS)
    post_comps_numbers(text, compound_names, NAME_BASE, SUFFIX_TYPE_LIST, TWO_WORD_NAME_TERMINI, EXCLUDED_NAMES,
                       SEPARATORS, range_compound_names)
    # print(range_compound_names)
    # single_comps(text, compound_names, NAME_BASE, SUFFIX_TYPE_LIST, TWO_WORD_NAME_TERMINI, EXCLUDED_NAMES, TERMINATORS)
    # Very inaccurate, introduces many error entries. This is because it can match without a (1)
    return sorted(compound_names + range_compound_names)



def clean_detected_items(abstract_text):
    """ Cleans out Compound classes from the chemical compound entities
            :param abstract_text: raw string of abstract text
            :return: list of names of cleaned detected chemical compounds
            """
    detected_chemical_names = name_search(abstract_text)
    clean_detected_names = []
    for x in detected_chemical_names:
        upper_item = x[0].upper()
        if upper_item in COMPOUND_CLASS:
            continue
        else:
            clean_detected_names.append(x)
    # print("detected_chemical_names: ", detected_chemical_names)
    return clean_detected_names


def article_compound_number(abstract_text):
    """ Detect the number of compound in the article
        :param abstract_text: raw string of abstract text
        :return: number of detected chemical compounds and list of names of detected chemical compounds
        """
    detected_chemical_names = name_search(abstract_text)
    clean_detected_chem_names = clean_detected_items(detected_chemical_names)
    list_length = len(clean_detected_chem_names)
    return clean_detected_chem_names, list_length


def improper_parentheses_capture(chem_list):
    """ Method to remove invalid parentheses, putting above 3 functions together
                        :param chem_list: list of chemicals(strings) as tuples with match index
                        :return: False if open bracket otherwise 0 when valid parentheses
                        """
    chemical_detection_list_no_invalid_parentheses = []

    if isinstance(chem_list, list):
        for chemical in chem_list:
            try:
                if bracket_matched(chemical[0]) is False:
                # if miscellaneous_functions.bracket_matched(chemical[0]) is False:
                    no_invalid_parentheses = remove_invalid_parentheses(chemical[0])
                    # no_invalid_parentheses = miscellaneous_functions.remove_invalid_parentheses(chemical[0])
                    chemical_detection_list_no_invalid_parentheses.append((
                        (no_invalid_parentheses[:1].upper() + no_invalid_parentheses[1:]), chemical[1]))
                else:
                    chemical_detection_list_no_invalid_parentheses.append(chemical)
            except TypeError as e:
                # print("no list ", chemical)
                continue
        unique_chemical_detection_list = list(set(chemical_detection_list_no_invalid_parentheses))
        return unique_chemical_detection_list


def chem_ner_prototype(abstract_text):
    """ Detect the compounds in the article ONLY!!! works for abstracts with compound names listed in groups
    (e.g. Examplamides A - C)
            :param abstract_text: raw string of abstract text
            :return: tuple contains with: compound name, match object index and abstract text with compound placeholders
            """
    if isinstance(abstract_text, str):
        chemical_detection_list = clean_detected_items(abstract_text)
        chemical_detection_list_no_open_parentheses = improper_parentheses_capture(chemical_detection_list)
        number_of_detected_chemical_names = len(chemical_detection_list_no_open_parentheses)
        # print("chemical_detection_list_no_open_parentheses: ", chemical_detection_list_no_open_parentheses)

        new_text_chem_list = []

        for idx, chem in enumerate(chemical_detection_list_no_open_parentheses):
            match_index = chem[1]
            comp_number = str(idx + 1)

            try:
                new_text = chem[2][:match_index[0]] + "comp_{0} ".format(comp_number) + chem[2][match_index[1]:]
                new_text_chem_list.append((chem[0], chem[1], new_text))

            except IndexError as error:
                print(error)
                # continue
        return new_text_chem_list

    else:
        return []


def match_root_name_in_abstract(abstract_text, root_name_list):

    match_res = [comp for comp in root_name_list if(comp in abstract_text)]
    if match_res:
        match_res = list(set([x.capitalize() for x in match_res]))
        match_res.sort()
        return match_res
    else:
        return []


def exclude_compound_name_check(root_name, match_end_index, abstract_text):

    abstract_tokens = nltk.word_tokenize(abstract_text[match_end_index:])

    if abstract_tokens and re.match(r"[a-zA-Z0-9αβγδ\+\(\)\-]", root_name):
        
        for i in EXCLUDED_NAMES:
            if re.match(r"%s[s]{0,1}" % i.lower(), abstract_tokens[0]):
                return 1
    
        for i in EXCLUDED_PART_OF_NAMES:
            if i.lower() in root_name:
                # print("exlude 2")
                return 1
        
        for i in EXCLUDED_NAMES:
            if root_name.lower() == i.lower() or (len(root_name) - len(i) == 1 and root_name[len(root_name)-1] == "s"):
                # print("exlude 4")
                return 1

        for i in COMPOUND_CLASS:
            if root_name.lower() == i.lower() or (len(root_name) - len(i) == 1 and root_name[len(root_name)-1] == "s"):
                # print("exlude 5")
                return 1
        
        # Compound name ends on a dash
        if root_name[len(root_name)-1] == "-":
            # print("ends on a dash")
            return 1
        
        # Compound name contains a slash
        if "/" in root_name:
            return 1

    # else:
        # TODO there can be more cases.
    return 0


def chem_ner_by_root_name(abstract_text, root_name_list):

    match_list_1 = []
    match_object_list_1 = []
    match_list_2 = []
    match_object_list_2 = []
    match_list_3 = []
    match_list_4 = []
    match_object_list_4 = []
    new_text_chem_list = []

    match_root_list = match_root_name_in_abstract(abstract_text, root_name_list)
    
    if match_root_list:

        for root in match_root_list:

            # print(root)
            flag = 0
            exclude_flag_1 = 0
            exclude_flag_3 = 0
            exclude_flag_4 = 0
            first_letter = root[0]
            first_letter_variation = [first_letter.upper(), first_letter.lower()]
            after_first_letter = root[1:]

            try:
                matching_compound_2 = re.finditer(r'(?:\w+)?%s%s[s]{0,1}\s(?:\()?[A-Z]{1,2}(?:\d{1,2})?-[A-Z]{1,2}(?:\d{1,2})?(?![A-Z])(?!\d+)' % (first_letter_variation, after_first_letter), abstract_text)
                
                for match in matching_compound_2:
                    # print(match, root)

                    split_name = re.split(r"\W", match[0])
                    while True:
                        try:
                            split_name.remove("")
                        except:
                            break
                    
                    root_name_index = 0
                    root_name = ""
                    range_list = []
                    for name in split_name:
                        if re.match(r"^[A-Z]{1,2}(?:\d{1,2})?$", name):
                            range_list.append(name)
                        else:
                            root_name_index = root_name_index + 1

                    root_name = " ".join([split_name[i] for i in range(0, root_name_index)])
                    
                    if len(root_name) > len(root) and re.match(r".*s$", root_name):
                        root_name = root_name[:len(root_name)-1]

                    if len(range_list) == 2:

                        if re.match(r"^[A-Z]{1,2}\d{1,2}$", range_list[0]) and re.match(r"^[A-Z]{1,2}\d{1,2}$", range_list[1]):
                            if len(range_list[0]) == len(range_list[0]):
                                range_len = len(range_list[0])
                                range_start = range_list[0]
                                range_end = range_list[1]

                                temp_root_name = root_name.capitalize() + " "

                                for i in range(0, range_len):
                                    if range_start[i].isalpha():
                                        if range_start[i] != range_end[i]:
                                            break
                                        else:
                                            temp_root_name = temp_root_name + range_start[i]

                                    elif range_start[i].isdigit():
                                        if ord(range_start[i]) > ord(range_end[i]):
                                            break
                                        elif range_start[i] == range_end[i]:
                                            temp_root_name = temp_root_name + str(range_start[i])
                                        else:
                                            temp_compound_names_list = []
                                            match_escaped = re.escape(match[0])
                                            comp_range_check = re.findall(r"%s(?:\s)?(?:\()?\d+(?:\s)?\-(?:\s)?\d+(?:\s)?(?:\))?" % match_escaped, abstract_text)

                                            if comp_range_check:
                                                comp_range_count = 0
                                                number_range = re.findall(r"\d+", comp_range_check[0])

                                                if len(number_range) == 2:
                                                    for i in range(int(number_range[0]), int(number_range[1])+1):
                                                        comp_range_count = comp_range_count + 1

                                                for num in range(ord(range_start[i]), ord(range_end[i]) + 1):
                                                    match_list_2.append((temp_root_name + chr(num), match.span(), abstract_text))
                                                    chem_name = temp_root_name + chr(num)
                                                    # if chem_name not in compound_names_list:
                                                    temp_compound_names_list.append((chem_name, match.span(), abstract_text))
                                                
                                                if comp_range_count == 0 or comp_range_count == len(temp_compound_names_list):
                                                    for chem in temp_compound_names_list:
                                                        match_list_2.append(chem)

                                                    match_object_list_2.append(match)

                                            else:
                                                for num in range(ord(range_start[i]), ord(range_end[i]) + 1):
                                                    match_list_2.append((temp_root_name + chr(num), match.span(), abstract_text))

                                                match_object_list_2.append(match)


                        elif re.match(r"^[A-Z]{1}$", range_list[0]) and re.match(r"^[A-Z]{1}$", range_list[1]):

                            temp_compound_names_list = []
                            match_escaped = re.escape(match[0])
                            comp_range_check = re.findall(r"%s(?:\s)?(?:\()?\d+(?:\s)?\-(?:\s)?\d+(?:\s)?(?:\))?" % match_escaped, abstract_text)

                            if comp_range_check:
                                comp_range_count = 0
                                number_range = re.findall(r"\d+", comp_range_check[0])

                                if len(number_range) == 2:
                                    for i in range(int(number_range[0]), int(number_range[1])+1):
                                        comp_range_count = comp_range_count + 1
                                # print(comp_range_count)

                                for char in range(ord(range_list[0]), ord(range_list[1]) + 1):
                                    temp_compound_names_list.append((root_name.capitalize() + " " + chr(char).upper(), match.span(), abstract_text))
                                
                                if comp_range_count == 0 or comp_range_count == len(temp_compound_names_list):
                                    for chem in temp_compound_names_list:
                                        match_list_2.append(chem)

                                    match_object_list_2.append(match)
     
                            else:
                                for char in range(ord(range_list[0]), ord(range_list[1]) + 1):
                                    match_list_2.append((root_name.capitalize() + " " + chr(char).upper(), match.span(), abstract_text))
  
                                match_object_list_2.append(match)

                matching_compound_1 = re.finditer(r"(?:\S+)?%s%s[s]{0,1}\s(\b(?:\d{1,2})?[A-Z]{1,3}(?:\d{1,3})?\b|\b[IXV]{1,5}\b)" % (first_letter_variation, after_first_letter),abstract_text)
                for match in matching_compound_1:
                    # print(root, " 1 ", match, match.start())

                    root_name_index = 0
                    root_name = ""
 
                    left_bracket = re.findall("\(", match[0])
                    right_bracket = re.findall("\)", match[0])

                    if  len(left_bracket) == len(right_bracket):
                        root_name = match[0]
                    else:
                        if len(left_bracket) < 2 and len(right_bracket) < 2:
                            if len(left_bracket) > len(right_bracket):
                                root_name = match[0].strip("(")
                                
                            elif len(left_bracket) < len(right_bracket):
                                root_name = match[0].strip(")")
                    
                    split_name = re.split(r"\s", root_name)
                    if len(split_name) == 2:

                        if re.match(r"[a-zA-Z\s]", root_name):
                            root_name = split_name[0].capitalize()
                        else:
                            root_name = split_name[0]
                            
                        if len(root_name) > len(root) and re.match(r".*s$", root_name):
                            root_name = root_name[:len(root_name)-1] + " " + split_name[1]
                        else:
                            root_name = root_name + " " + split_name[1]
                    
                    elif len(split_name) == 3 and ("acid" in split_name[1]):
                            root_name = split_name[0][0].upper() + split_name[0][1:] + " " + split_name[1].rstrip("s") + " " + split_name[2]
                        
                    flag = 0

                    if len(match_object_list_1) > 0 or len(match_object_list_2) > 0:
                        for i in match_list_2:
                            if root_name.lower() in i[0].lower():
                                flag = 1
                                break

                        for j in match_object_list_1:
                            if match.start() >= j.start() and match.end() <= j.end():
                                flag = 1
                                break
                    
                    if flag == 0:
                        exclude_flag_1 = 0
                        exclude_flag_1 = exclude_compound_name_check(root_name, match.start(), abstract_text)

                        if exclude_flag_1 == 0:
                            match_list_1.append((root_name, match.span(), abstract_text))
                            match_object_list_1.append(match)


                matching_compound_4 = re.finditer(r"(?:\S+)?%s%s[s]{0,1}(?:[^\s.]+)?" % (first_letter_variation, after_first_letter), abstract_text)
                for match in matching_compound_4:
                    # print(root, " 4 ", match, match.start())

                    root_name = match[0]
                    if re.match(r"[.,;]", root_name[len(root_name)-1]):
                        root_name = root_name[:len(root_name)-1]

                    left_bracket = re.findall("\(", root_name)
                    right_bracket = re.findall("\)", root_name)
                    
                    if  len(left_bracket) != len(right_bracket):
                        # print(len(left_bracket),  len(right_bracket))
                        if len(left_bracket) < 2 and len(right_bracket) < 2:
                            if len(left_bracket) > len(right_bracket):
                                root_name = root_name.strip("(")
                                
                            elif len(left_bracket) < len(right_bracket):
                                root_name = root_name.strip("),")
                        
                        elif len(left_bracket) - len(right_bracket) == 1:
                            if root_name[0] == "(":                            
                                root_name = root_name[1:]

                        elif len(right_bracket) - len(left_bracket) == 1:
                                if root_name[len(root_name)-1] == ")":               
                                    root_name = root_name[:len(root_name)-1]
                                elif root_name[len(root_name)-1] == "),":             
                                    root_name = root_name[:len(root_name)-2]

                    elif len(left_bracket) == 1 and len(right_bracket) == 1:
                        if root_name[0] == "(" and root_name[len(root_name)-1] == ")":
                            root_name = root_name.strip("(")
                            root_name = root_name.strip(")")
                    
                    flag = 0
                    if re.match(r".*ins$", root_name) or re.match(r".*iods$", root_name):
                        flag = 1

                    if len(match_object_list_1) > 0 or len(match_object_list_2) > 0 or len(match_object_list_4) > 0:
                        for i in match_object_list_1:
                            if match.start() >= i.start() and match.end() <= i.end():
                                flag = 1
                                break
                        
                        for i in match_list_1:
                            if root_name.lower() in i[0].lower():
                                flag = 1
                                break
                        
                        for j in match_object_list_2:
                            if root_name.lower() in j[0].lower():
                                flag = 1
                                break
                        
                        for k in match_object_list_4:
                            if root_name.lower() in k[0].lower() and match.start() >= k.start() and match.end() <= k.end():
                                flag = 1
                                break

                    if len(root_name) > len(root) and re.match(r".*ic$", root_name):
                        flag = 1
                    
                    if flag == 0:
                        if re.match(r"[a-zA-Z]", root_name[0]):   
                            exclude_flag_4 = exclude_compound_name_check(root_name, match.end(), abstract_text)
                    
                            if exclude_flag_1 == 0 and exclude_flag_4 == 0:
                                
                                match_list_4.append((root_name[0].upper()+root_name[1:], match.span(), abstract_text))
                                match_object_list_4.append(match)
 
                        else:
                            if len(root_name) > len(root) and re.match(r".*s$", root_name):
                                root_name = root_name[:len(root_name)-1]
                            
                            exclude_flag_4 = exclude_compound_name_check(root_name, match.end(), abstract_text)

                            if exclude_flag_1 == 0 and exclude_flag_4 == 0:
                                match_list_4.append((root_name, match.span(), abstract_text))
                                match_object_list_4.append(match)

                matching_compound_3 = re.finditer(r"\s(%s%s)\s" % (first_letter_variation, after_first_letter), abstract_text)   
                flag = 0
                for match in matching_compound_3:
                    # print(root, " 3 ", match, match.start())
                
                    exclude_flag_3 = 0
                    if len(match_object_list_2) > 0 or len(match_object_list_1) > 0 or len(match_object_list_4) > 0:
                        for i in match_object_list_2:
                            if match.group(1).lower() in i[0].lower():
                                flag = 1
                                break

                        for j in match_object_list_1:
                            if match.start(1) >= j.start() and match.end(1) <= j.end():
                                flag = 1
                                break

                        for k in match_object_list_4:
                            if match.start(1) >= k.start() and match.end(1) <= k.end():
                                flag = 1
                                break

                    if flag == 0:
                        exclude_flag_3 = exclude_compound_name_check(match.group(1), match.end(1), abstract_text)
                        if exclude_flag_4 == 0 and exclude_flag_3 == 0:
                            match_list_3.append((match.group(1).capitalize(), match.span(1), abstract_text))
            
            except TypeError as e:
                print(e)
            except AttributeError as e2:
                print(e2)
            except ValueError as e3:
                print(e3)
            except IndexError as e4:
                print(e4)


        comp_list = match_list_1 + match_list_2 + match_list_3 + match_list_4
        temp_comp_list = comp_list
        # print(temp_comp_list)
        
        if comp_list:
            for i in comp_list:
                for j in comp_list:
                    if i[1][0] == j[1][0]:
                        if len(i[0]) > len(j[0]):
                            # print(i[0], j[0], i[1][0])
                            temp_comp_list.remove(j)

            for idx, chem in enumerate(temp_comp_list):
                match_index = chem[1]
                comp_number = str(idx + 1)

                new_text = chem[2][:match_index[0]] + "comp_{0} ".format(comp_number) + chem[2][match_index[1]:]
                new_text_chem_list.append((chem[0], chem[1], new_text))
            # print(new_text_chem_list)

    # print("new_text_chem_list: ", new_text_chem_list)
    return new_text_chem_list
    


def get_compound(abstract_text, root_name_list):
    """For the detection of compound entities by using root names.
                        :param abstract_text: raw string of abstract text
                        :param root_name_list: list of all root names
                        :return: []
                        """
    if isinstance(abstract_text, str):
        return chem_ner_by_root_name(abstract_text, root_name_list)
    else:
        return []
