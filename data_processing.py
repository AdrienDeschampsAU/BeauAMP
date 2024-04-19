# pose problème car on prend les données dans l'observation d'avant

import pandas as pd
from datetime import datetime
import pickle
import numpy as np
import re
import json
import urllib
import urllib.request
import ast


# We first define the functions we will need :

def remove_backslash(data):
    replacements = {
        '\\\\"}': '"}',
        '\\\\",': '\",',
        '\\T': '',
        '\\N': '',
        '\\"': '',
        '\\\\}': '}',
        '\\t': '',
        '\\n': '',
    }
    for old, new in replacements.items():
        data = data.replace(old, new)
    return data


def get_data(data, key):
    return data.get(key, '')


def get_data_procedure(data):
    return get_data(data, 'PROCEDURE')


def get_data_award(data):
    return get_data(data, 'ATTRIBUTION')


def get_data_object(data):
    return get_data(data, 'OBJET')


def get_data_identity(data):
    return get_data(data, 'IDENT') or get_data(data, 'IDENTITE')


def get_data_category(data):
    if 'TYPE_POUVOIR_ADJUDICATEUR' in data:
        return get_data(data, 'TYPE_POUVOIR_ADJUDICATEUR')
    else:
        return get_data(data, 'TYPE_ORGANISME')


def get_main_activity(data):
    return get_data(data, 'ACTIVITE_PRINCIPALE')


def get_previous_data(data):
    return get_data(data, 'PUBLICATION_ANTERIEURE')


def get_cae_siret(data):
    if type(data) == dict:
        return check_id(str(data.get('CODE_IDENT_NATIONAL', '')))
    elif type(data) == list:
        list_id = []
        for cae in data:
            list_id.append(check_id(str(cae.get('CODE_IDENT_NATIONAL', ''))))
        return list_id
    else:
        return ''


def get_cae_address(data):
    if type(data) == dict:
        return data.get('ADRESSE', '')
    elif type(data) == list:
        list_address = []
        for cae in data:
            list_address.append(cae.get('ADRESSE', ''))
        return list_address
    else:
        return ''


def get_cae_town(data):
    if type(data) == dict:
        return data.get('VILLE', '')
    elif type(data) == list:
        list_town = []
        for cae in data:
            list_town.append(cae.get('VILLE', ''))
        return list_town
    else:
        return ''


def get_cae_zip(data):
    if type(data) == dict:
        return data.get('CP', '')
    elif type(data) == list:
        list_zip = []
        for cae in data:
            list_zip.append(cae.get('CP', ''))
        return list_zip
    else:
        return ''


def get_cae_category(data):
    category = ''
    try:
        if data != '':
            category = list(data.items())[0][0]
            if category == 'AUTRE':
                category = data['AUTRE']
    except:
        pass
    return category


def get_name_activity(data, key):
    activity = next(iter(data[key]))
    if activity == 'AUTRE':
        activity = data[key]['AUTRE']
    return activity


def get_cae_activity(data):
    for key in ['POUVOIR_ADJUDICATEUR', 'ENTITE_ADJUDICATRICE']:
        if key in data:
            return get_name_activity(data, key)
    return ''


def type_reserved_contract(data):
    if 'ATELIERS_PROTEGES' in data:
        if 'EMPLOIS_PROTEGES' in data:
            return 'workshop & jobs'
        else:
            return 'workshop'
    elif 'EMPLOIS_PROTEGES' in data:
        return 'jobs'
    else:
        return False


def get_number_corrections(data):
    previous_information = data.get('MARCHE', {}).get('ANNONCE_ANTERIEUR', '')
    if isinstance(previous_information, dict):
        return 0
    elif isinstance(previous_information, list):
        return len(previous_information) - 1
    return ''


def get_estimated_price(data):
    estimation_information = data.get('ESTIMATION_INITIALE', {})
    if isinstance(estimation_information, dict):
        estimation = estimation_information.get('#TEXT', '')
        return float(estimation) if estimation.replace('.', '', 1).isdigit() else ''
    return ''


def get_award_price(data):
    price_information = data.get('MONTANT', {})
    if isinstance(price_information, dict):
        price = price_information.get('#TEXT', '')
        return float(price) if price.replace('.', '', 1).isdigit() else ''
    return ''


def get_CPV(data):
    try:
        if isinstance(data, dict):
            return data.get('PRINCIPAL', '')
        elif isinstance(data, list):
            return [i.get('PRINCIPAL', '') for i in data]
    except Exception:
        return ''


def get_min_offer(data):
    min_offer_information = data.get('OFFRE_BASSE', {})
    if isinstance(min_offer_information, dict):
        min_offer = min_offer_information.get('#TEXT', '')
        return float(min_offer) if min_offer.replace('.', '', 1).isdigit() else ''
    return ''


def get_max_offer(data):
    max_offer_information = data.get('OFFRE_ELEVEE', {})
    if isinstance(max_offer_information, dict):
        max_offer = max_offer_information.get('#TEXT', '')
        return float(max_offer) if max_offer.replace('.', '', 1).isdigit() else ''
    return ''


def get_number_offers(data):
    try:
        number= data.get('NB_OFFRE_RECU', '')
        return int(number)
    except ValueError:
        return ''


def get_on_behalf(data):
    try:
        return True if "AGIT_POUR_AUTRE_COMPTE_OUI" in data else False if "AGIT_POUR_AUTRE_COMPTE_NON" in data else ''
    except Exception:
        return ''


def get_central_procurement(data):
    try:
        return True if "ORGANISME_ACHETEUR_CENTRAL_OUI" in data else False if "ORGANISME_ACHETEUR_CENTRAL_NON" in data else ''
    except Exception:
        return ''


def get_framework_agreement(data):
    try:
        return True if '"ACCORD_CADRE"' in data or "ACCORD_CADRE_OUI" in data else False
    except Exception:
        return ''


def get_accelerated_procedure(data):
    try:
        procedure_type = data.get('TYPE_PROCEDURE', {})
        return any('ACCELERE' in procedure_type.get(key, {}) for key in ['OUVERT', 'RESTREINT', 'NEGOCIE'])
    except Exception:
        return ''


def get_number_offers_SME(data):
    try:
        number = data.get('NB_OFFRE_RECU_PME', '')
        return int(number)
    except ValueError:
        return ''


def get_number_offers_UE(data):
    try:
        number = data.get('NB_OFFRE_RECU_UE', '')
        return int(number)
    except ValueError:
        return ''


def get_number_offers_non_EU(data):
    try:
        number = data.get('NB_OFFRE_RECU_NON_UE', '')
        return int(number)
    except ValueError:
        return ''


def get_subcontracting(data):
    return True if 'SOUSTRAITANCE_OUI' in data else False if 'SOUSTRAITANCE_NON' in data else ''


def get_AGP(data):
    return True if 'AMP_OUI' in data else False if 'AMP_NON' in data else ''


list_missing_criteria = [
    "LE PRIX N'EST PAS LE SEUL",
    "CRITERES_CCTP"]

list_price_synonyms = [
    'PRIX',
    'COUT',
    'COÛT',
    'FINANCIE',
    'FINANCIÈ',
    'MONTANT',
    'TARIF']


def price_criterion_detection(data):
    return any(key in data for key in list_price_synonyms)


def criteria_presence_detection(data):
    presence = any(key in data for key in list_missing_criteria)
    return not presence and '"CRITERES_ATTRIBUTION"' in data


def is_number(data):
    try:
        float(data)
        return True
    except ValueError:
        return False


def make_number(data):
    decimal = False
    weight = ''.join(i if i.isdigit() else '.' if (i == ',' or i == '.') and not decimal else '' for i in data)
    return weight if is_number(weight) else ''

accepted_sums = [
    1,
    10,
    20,
    100
    ]


def checking_criteria(quality, price):
    try:
        if type(quality) == list:
            sum_weights = float(price) + sum(float(criterion) for criterion in quality)
        else:
            sum_weights = float(price) + float(quality)
        if sum_weights in accepted_sums:
            adjusted_price = 100 * float(price) / sum_weights
            if type(quality) == list:
                adjusted_quality = [100 * float(criterion) / sum_weights for criterion in quality]
            else:
                adjusted_quality = [100 * float(quality) / sum_weights]
            return True, adjusted_quality, adjusted_price
    except ValueError:
        pass
    return False, '', ''


def listing_lot_criteria(data):
    price_criterion = ''
    quality_text = ''
    quality_weights = ''
    try:
        information = data['CRITERES_ATTRIBUTION']
        if len(information) == 1:
            if 'CRITERES_COUT' in data['CRITERES_ATTRIBUTION'] or 'CRITERES_PRIX' in data['CRITERES_ATTRIBUTION']:
                return ('', 0, 100)
        elif len(information) == 2:
            quality_information = information['CRITERES_QUALITE']['CRITERE']
            if type(quality_information) == dict:
                if not price_criterion_detection(quality_information['#TEXT']):
                    quality_text = quality_information['#TEXT']
                    if '@POIDS' in quality_information:
                        quality_weights = quality_information['@POIDS']
                    else:
                        quality_weights = quality_information['POIDS']
                    if not is_number(quality_weights):
                        quality_weights = make_number(quality_weights)
            else:
                list_quality_text = []
                list_quality_weight = []
                for criterion in quality_information:
                    text = criterion['#TEXT']
                    if not price_criterion_detection(text):
                        list_quality_text.append(text.replace(',', ''))
                        if 'POIDS' in criterion:
                            if is_number(criterion['POIDS']):
                                list_quality_weight.append(criterion['POIDS'])
                            else:
                                weight = make_number(criterion['POIDS'])
                                if weight != '':
                                    list_quality_weight.append(weight)
                                else:
                                    list_quality_weight.append('?')
                        else:
                            if is_number(criterion['@POIDS']):
                                list_quality_weight.append(criterion['@POIDS'])
                            else:
                                weight = make_number(criterion['@POIDS'])
                                if weight != '':
                                    list_quality_weight.append(weight)
                                else:
                                    list_quality_weight.append('?')
                quality_text = list_quality_text
                quality_weights = list_quality_weight
            if 'CRITERES_COUT' in information:
                price_criterion = list((data['CRITERES_ATTRIBUTION']['CRITERES_COUT']['CRITERE']).values())[0]
            else:
                price_criterion = list((data['CRITERES_ATTRIBUTION']['CRITERES_PRIX'].values()))[0]
            if not is_number(price_criterion):
                price_criterion = make_number(price_criterion)
    except:
        pass
    if not checking_criteria(quality_weights, price_criterion)[0]:
        return (quality_text, '', '')
    else:
        adjusted_quality_weights = checking_criteria(quality_weights, price_criterion)[1]
        ajusted_price_weight = checking_criteria(quality_weights, price_criterion)[2]
        return (quality_text, adjusted_quality_weights, ajusted_price_weight)


def listing_procedure_criteria(data):
    criteria = ''
    quality_weight = ''
    price_weight = ''
    try:
        ranked = False
        if 'CRITERES_PONDERES' in data['CRITERES_ATTRIBUTION']:
            criteria_information = data['CRITERES_ATTRIBUTION']['CRITERES_PONDERES']['CRITERE']
        elif 'CRITERES_PRIORITES' in data['CRITERES_ATTRIBUTION']:
            criteria_information = data['CRITERES_ATTRIBUTION']['CRITERES_PRIORITES']['CRITERE']
            ranked = True
        list_criteria = []
        list_weights = []
        for key in criteria_information:
            weight = ''
            if not price_criterion_detection(key['#TEXT']):
                list_criteria.append(key['#TEXT'].replace(',', ''))
                if not ranked:
                    weight = list(key.values())[0]
                    if not is_number(weight):
                        list_weights.append(make_number(weight))
                    else:
                        list_weights.append(weight)
            else:
                if not ranked:
                    price_weight = list(key.values())[0]
                    if not is_number(price_weight):
                        price_weight = make_number(price_weight)
        criteria = list_criteria
        quality_weight = list_weights
    except:
        pass
    if not checking_criteria(quality_weight, price_weight)[0]:
        return (criteria, '', '')
    else:
        adjusted_quality_weight = checking_criteria(quality_weight, price_weight)[1]
        adjusted_weight_price = checking_criteria(quality_weight, price_weight)[2]
        return (criteria, adjusted_quality_weight, adjusted_weight_price)


def make_date(data):
    try:
        data = data.split('-')
        data[0] = '20' + data[0] if data[0] in [str(i) for i in range(15, 24)] else data[0]
        return '-'.join(data)
    except:
        return ''


def get_award_date(data):
    test = data.get('DATE_ATTRIBUTION', '')
    return make_date(test) if len(test) != 10 else test


def get_environmental_clause(data):
    return 'environnementaux' in data if not isinstance(data, float) else False


def get_social_clause(data):
    return 'sociaux' in data if not isinstance(data, float) else False


date_format = '%Y-%m-%d'

def get_advertising_duration(date, data):
    try:
        delay = data.get('CONDITION_DELAI', {})
        if isinstance(delay, dict):
            end = delay.get('RECEPT_OFFRES', '')
            end = datetime.strptime(end[:10], date_format)
            duration = (end - date).days
            return duration if duration > 0 else ''
    except:
        return ''


def get_call_id(data):
    try:
        contract = data.get('MARCHE', {})
        previous_information = contract.get('ANNONCE_ANTERIEUR', [])
        previous_information = [previous_information] if isinstance(previous_information, dict) else previous_information
        for publication in previous_information:
            reference = publication.get('REFERENCE', {})
            notice_type = reference.get('TYPE_AVIS', {})
            if 'INITIAL' in notice_type.get('STATUT', ''):
                return reference.get('IDWEB', '')
    except:
        pass
    return ''


def get_delivery_site(data):
    if isinstance(data, dict):
        lieu_exec_livr = data.get('LIEU_EXEC_LIVR', {})
        if isinstance(lieu_exec_livr, dict):
            return ' '.join([str(value) for value in lieu_exec_livr.values()])
    return ''


liste_chiffres = [
    'UN',
    'DEUX',
    'TROIS',
    'QUATRE',
    'CINQ',
    'SIX',
    'SEPT',
    'HUIT',
    'NEUF']


list_words_to_ignore = ['LOT', 'N°', 'NUM', 'NUMERO', 'NUMÉRO', 'NO']

def convert_to_digits(data):
    for i, number in enumerate(liste_chiffres, start=1):
        if 'UNIQ' not in data:
            data = re.sub(number, str(i), data)
    for key in list_words_to_ignore + [' ']:
        data = re.sub(key, '', data)
    data = re.sub(r'0([1-9])', r'\1', data)
    return data


def lot_object_analysis(data, criteria_presence):
    dictionary = {}
    if 'INTITULE' in data:
        dictionary['INTITULE'] = data['INTITULE']
    if 'DESCRIPTION' in data:
        dictionary['DESCRIPTION'] = data['DESCRIPTION']
    if 'NUM' in data:
        dictionary['ID_LOT'] = convert_to_digits(data['NUM'])
    if 'CPV' in data:
        dictionary['CPV'] = get_CPV(data['CPV'])
    if 'FONDS_COMMUNAUTAIRES_OUI' in data:
        dictionary['EU_FUNDS'] = True
    elif 'FONDS_COMMUNAUTAIRES_NON' in data:
        dictionary['EU_FUNDS'] = False
    if 'CODE_NUTS' in data:
        dictionary['EXECUTION_NUTS'] = data['CODE_NUTS']
    if 'LIEU_PRINCIPAL' in data:
        dictionary['EXECUTION_SITE'] = data['LIEU_PRINCIPAL']
    if criteria_presence and 'CRITERES_ATTRIBUTION' in data:
        criteria = listing_lot_criteria(data)
        if criteria[0] != '':
            dictionary['Q_CRITERIA_TEXT'] = criteria[0]
        if criteria[1] != '':
            dictionary['Q_CRITERIA_WEIGHTS'] = criteria[1]
        if criteria[2] != '':
            dictionary['P_CRITERION_WEIGHT'] = criteria[2]
    return dictionary


def lot_award_analysis(data):
    outcome = 'awarded' if 'ATTRIBUE' in data else 'unsuccessful' if 'INFRUCTUEUX' in data else 'cancelled' if 'SANS_SUITE' in data else 'not_found'
    dictionary = {
        'DESCRIPTION': data.get('DESCRIPTION', ''),
        'INTITULE': data.get('INTITULE', ''),
        'ID_LOT': convert_to_digits(data.get('NUM_LOT', '')),
        'OUTCOME': outcome,
    }
    if outcome == 'awarded' and 'RENSEIGNEMENT' in data:
        information = data.get('RENSEIGNEMENT', {})
        if isinstance(information, dict):
            dictionary.update({
                'NUMBER_OFFERS': get_number_offers(information),
                'NUMBER_OFFERS_SME': get_number_offers_SME(information),
                'ESTIMATED_PRICE': get_estimated_price(information),
                'AWARD_PRICE': get_award_price(information),
                'MIN_OFFER': get_min_offer(information),
                'MAX_OFFER': get_max_offer(information),
                'SUBCONTRACTING': get_subcontracting(information),
                'AWARD_DATE': get_award_date(information),
                'NUMBER_EU_OFFERS': get_number_offers_UE(information),
                'NUMBER_NON_EU_OFFERS': get_number_offers_non_EU(information),
                'BUSINESS_ASSOCIATION': 'GROUPEMENT_ECONOMIQUE' in information
            })
    return dictionary


def winner_analysis(data, multi):
    return {
        'WIN_SIRET': check_id(str(data.get('CODE_IDENT_NATIONAL', ''))),
        'WIN_STATED_NAME': data.get('DENOMINATION', ''),
        'WIN_ADDRESS': data.get('ADRESSE', ''),
        'WIN_TOWN': data.get('VILLE', ''),
        'WIN_ZIP_CODE': data.get('CP', ''),
        'WIN_COUNTRY_CODE': data.get('PAYS', ''),
        'CONTRACTOR_SME': True if 'PME_OUI' in data else False if 'PME_NON' in data else '',
        'EU_FUNDS': data.get('FONDS_COMMUNAUTAIRES_OUI', False),
        'MULTI_WIN': multi
    }


def merge(dic1, dic2):
    dic3 = {**dic1, **dic2}
    return dic3


def object_analysis(data, criteria_presence):
    dictionary = {}
    if 'NUM' in data:
        dictionary['ID_LOT'] = convert_to_digits(data['NUM'])
    if 'DUREE_MOIS' in data:
        dictionary['DURATION'] = data['DUREE_MOIS']
    elif 'DUREE_JOURS' in data:
        dictionary['DURATION'] = int(data['DUREE_JOURS'])/30
    elif 'DUREE_DELAI' in data:
        if 'DUREE_MOIS' in data['DUREE_DELAI']:
            dictionary['DURATION'] = data['DUREE_DELAI']['DUREE_MOIS']
        elif 'DUREE_JOURS' in data['DUREE_DELAI']:
            dictionary['DURATION'] = int(data['DUREE_DELAI']['DUREE_JOURS'])/30
    if 'RENOUVELLEMENT_OUI' in data:
        dictionary['RENEWABLE'] = True
    elif 'RENOUVELLEMENT_NON' in data:
        dictionary['RENEWABLE'] = False
    if 'CODE_NUTS' in data:
        dictionary['EXECUTION_NUTS'] = data['CODE_NUTS']
    if 'LIEU_PRINCIPAL' in data:
        dictionary['EXECUTION_SITE'] = data['LIEU_PRINCIPAL']
    if 'CPV' in data:
        dictionary['CPV'] = get_CPV(data['CPV'])
    if criteria_presence and 'CRITERES_ATTRIBUTION' in data:
        if listing_lot_criteria(data)[0] != '':
            dictionary['Q_CRITERIA_TEXT'] = listing_lot_criteria(data)[0]
        if listing_lot_criteria(data)[1] != '':
            dictionary['Q_CRITERIA_WEIGHTS'] = listing_lot_criteria(data)[1]
        if listing_lot_criteria(data)[2] != '':
            dictionary['P_CRITERION_WEIGHT'] = listing_lot_criteria(data)[2]
    return dictionary


def comparing_titles(lot_object, lot_award):
    lot_object_name = lot_object.get('INTITULE', '')
    lot_object_description = lot_object.get('DESCRIPTION', '')
    lot_award_name = lot_award.get('INTITULE', '')
    lot_award_description = lot_award.get('DESCRIPTION', '')
    for variable_object in (lot_object_name, lot_object_description):
        if variable_object != '':
            for variable_award in (lot_award_name, lot_award_description):
                if variable_object == variable_award:
                    return True
    return False


environmental_lexicon = [
'ENVIRONNEM',
'ENVIRONEM',
'ECOLO',
'ÉCOLO',
'ÉCOSYST',
'ECOSYST',
'ÉCO-SYST',
'ECO-SYST',
'RECYCL',
'RECICL',
'SOUTENABI',
'DURAB',
'CLIMAT',
'CARBO',
'DUREE DE VIE',
'DURÉE DE VIE',
'POLLUT'
]

social_lexicon = [
'SOCIA',
'SOCIÉT',
'SOCIETA',
'ÉTHIQUE',
'ETHIQUE',
'TRACABILI',
'TRAÇABILI',
'INSERTION',
'HUMAIN',
' RSE',
'PERSONNEL'
]

delay_lexicon = [
'DELAI',
'DÉLAI',
'DURÉE',
'DUREE',
'PÉRIODE',
'PERIODE',
'TEMPS',
'PLANING',
'PLANNING'
]

quality_lexicon = [
    'QUALIT']

technical_lexicon = [
'TECHNIQUE',
'TECHNOLO',
'METHOD',
'MÉTHOD',
'QUALIT',
'FONCTION',
'EXECUTION',
'EXÉCUTION',
'ÉXÉCUTION',
'ÉXECUTION',
'OPÉRAT',
'OPERAT'
]


def find_criterion_type(data):
    if pd.isna(data):
        return np.nan
    for key in environmental_lexicon:
        if key in data:
            social = False
            for key in social_lexicon:
                if key in data:
                    social = True
                    break
            if social:
                return 'socio_environmental'
            else:
                return 'environmental'
            break
    for key in social_lexicon:
        if key in data:
            return 'social'
    for key in delay_lexicon:
        if key in data:
            return 'delay'
    for key in quality_lexicon:
        if key in data:
            return 'quality'
    for key in technical_lexicon:
        if key in data:
            return 'technical'
    return("other")


def apply_find_criterion_type(row):
    if row == '':
        return ''
    if isinstance(row, list):
        return [find_criterion_type(key) for key in row]
    elif isinstance(row, str):
        return find_criterion_type(row)


def check_id(id_string):
    cleaned_id = re.sub('\D', '', str(id_string))
    if len(cleaned_id) == 14:
        return cleaned_id
    else:
        return ''


def translate_types(lst):
    translation_dict = {'FOURNITURES': 'supplies', 'TRAVAUX': 'works', 'SERVICES': 'services'}
    if isinstance(lst, list):
        return [translation_dict.get(item, item) for item in lst]
    else:
        return lst


def compare_lengths(row):
    if isinstance(row['Q_CRITERIA_TEXT'], list) and isinstance(row['Q_CRITERIA_WEIGHTS'], list):
        return len(row['Q_CRITERIA_TEXT']) != len(row['Q_CRITERIA_WEIGHTS'])
    else:
        return False


# Downloading notices

list_departements = [
    '75',
    '59',
    '13',
    '92',
    '69',
    '93',
    '33',
    '78',
    '94',
    '62',
    '91',
    '76',
    '83',
    '77',
    '31',
    '95',
    '6',
    '34',
    '44',
    '38',
    '67',
    '35',
    '57',
    '60',
    '54',
    '45',
    '29',
    '74',
    '30',
    '42',
    '80',
    '27',
    '17',
    '14',
    '64',
    '84',
    '56',
    '73',
    '49',
    '51',
    '1',
    '68',
    '2',
    '63',
    '37',
    '974',
    '21',
    '85',
    '40',
    '50',
    '87',
    '28',
    '25',
    '72',
    '26',
    '86',
    '66',
    '71',
    '11',
    '22',
    '972',
    '971',
    '88',
    '10',
    '16',
    '20A',
    '47',
    '973',
    '18',
    '24',
    '79',
    '41',
    '55',
    '89',
    '3',
    '4',
    '7',
    '52',
    '61',
    '0',
    '65',
    '8',
    '20B',
    '58',
    '5',
    '82',
    '12',
    '81',
    '39',
    '19',
    '36',
    '90',
    '53',
    '43',
    '32',
    '70',
    '9',
    '46',
    '15',
    '23'
]

variables_api = [
    'idweb',
    'id',
    'annonce_reference_schema_v110',
    'objet',
    'Filename',
    'famille',
    'code_departement',
    'code_departement_prestation',
    'famille_libelle',
    'dateparution',
    'datefindiffusion',
    'datelimitereponse',
    'nomacheteur',
    'titulaire',
    'perimetre',
    'type_procedure',
    'soustype_procedure',
    'procedure_libelle',
    'procedure_categorise',
    'nature',
    'sousnature',
    'nature_libelle',
    'sousnature_libelle',
    'nature_categorise',
    'nature_categorise_libelle',
    'criteres',
    'marche_public_simplifie',
    'marche_public_simplifie_label',
    'etat',
    'descripteur_code',
    'dc',
    'descripteur_libelle',
    'type_marche',
    'type_marche_facette',
    'type_avis',
    'annonce_lie',
    'annonces_anterieures',
    'annonces_anterieures_schema_v110',
    'source_schema',
    'gestion',
    'donnees',
    'url_avis'
]


# First, downloading contract notices

print('--- Importing contract notices ---')

start_url_contract_notices = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/exports/json?lang=fr&refine=nature_categorise_libelle%3A%22Avis%20de%20march%C3%A9%22&refine=code_departement%3A%22'

end_url_contract_notices = '%22&timezone=Europe%2FBerlin'

contract_notices = pd.DataFrame(columns=variables_api)

for code in list_departements:
    url = start_url_contract_notices + code + end_url_contract_notices
    fichier = urllib.request.urlopen(url)
    data = json.loads(fichier.read().decode())
    contract_notices = pd.concat([contract_notices, pd.DataFrame(data)], ignore_index=True)
    print('"Département" ' + code + ' downloaded')

contract_notices = contract_notices.drop_duplicates(subset = 'idweb')
contract_notices = contract_notices[contract_notices['famille'].isin(('JOUE','FNS', 'MAPA'))]
contract_notices = contract_notices[['idweb', 'dateparution', 'donnees']]
contract_notices.set_index('idweb', inplace=True)


# Second, downloading award notices

print('--- Importing award notices ---')

début_url_r = 'https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/exports/json?lang=fr&refine=nature_categorise_libelle%3A%22R%C3%A9sultat%20de%20march%C3%A9%22&refine=code_departement%3A%22'

fin_url_r = '%22&timezone=Europe%2FBerlin'

award_notices = pd.DataFrame(columns=variables_api)

for code in list_departements:
    url = début_url_r + code + fin_url_r
    fichier = urllib.request.urlopen(url)
    data = json.loads(fichier.read().decode())
    award_notices = pd.concat([award_notices, pd.DataFrame(data)], ignore_index=True)
    print('département ' + code + ' traité')
award_notices = award_notices[award_notices['famille'].isin(('JOUE','FNS', 'MAPA'))]

award_notices = award_notices.drop_duplicates(subset = 'idweb')


# Data cleaning

print('--- Keeping only contracts from 2015 ---')
start_date = pd.to_datetime('2015-01-01')
end_date = pd.to_datetime('2023-12-31')
award_notices['dateparution'] = pd.to_datetime(award_notices['dateparution'])
award_notices = award_notices[award_notices['dateparution'].between(start_date, end_date)]

call_start_date = pd.to_datetime('2013-01-01')
contract_notices['dateparution'] = pd.to_datetime(contract_notices['dateparution'])
contract_notices = contract_notices[contract_notices['datepar''ution'] > call_start_date]

print('--- Cleaning text data ---')
award_notices['donnees'] = award_notices['donnees'].str.upper()
contract_notices['donnees'] = contract_notices['donnees'].str.upper()
award_notices['nomacheteur'] = award_notices['nomacheteur'].str.upper()
for dataframe in [award_notices, contract_notices]:
    dataframe['donnees'] = dataframe['donnees'].apply(remove_backslash)


# Definition of the variables we will extract

variables = [
    "ID_BOAMP_AWARD",
    "ID_BOAMP_CONTRACT",
    "AWARD_NOTICE_DATE",
    "CONTRACT_NOTICE_DATE",
    "ID_LOT",
    "THRESHOLD",
    "CONTRACT_TYPE",
    "PROCEDURE_TYPE",
    "ACCELERATED",
    "AGP",
    "ADVERTISING",
    "CORRECTIONS",
    "CPV",
    "OBJECT",
    "EXECUTION_SITE",
    "RENEWABLE",
    "DURATION",
    "NUMBER_LOTS",
    "ON_BEHALF",
    "RESERVED_CONTRACT",
    "CENTRAL_PROCUREMENT",
    "FRAMEWORK_AGREEMENT",
    "ESTIMATED_PRICE",
    "ENVIRONMENTAL_CLAUSE",
    "SOCIAL_CLAUSE",
    "Q_CRITERIA_TEXT",
    "Q_CRITERIA_TYPE",
    "Q_CRITERIA_WEIGHTS",
    "P_CRITERION_WEIGHT",
    "OUTCOME",
    "AWARD_DATE",
    "AWARD_PRICE",
    "MIN_OFFER",
    "MAX_OFFER",
    "NUMBER_OFFERS",
    "NUMBER_OFFERS_SME",
    "NUMBER_EU_OFFERS",
    "NUMBER_NON_EU_OFFERS",
    "MULTI_WIN",
    "BUSINESS_ASSOCIATION",
    "SUBCONTRACTING",
    "CAE_STATED_NAME",
    "CAE_SIRET",
    "CAE_SIRET_KNOWN",
    "CAE_ADDRESS",
    "CAE_TOWN",
    "CAE_ZIP_CODE",
    "CAE_STATED_TYPE",
    "CAE_STATED_ACTIVITY",
    "WIN_STATED_NAME",
    "WIN_SIRET",
    "WIN_SIRET_KNOWN",
    "WIN_ADDRESS",
    "WIN_TOWN",
    "WIN_ZIP_CODE",
    "WIN_COUNTRY_CODE",
    "CONTRACTOR_SME",
    "EXECUTION_NUTS",
    "DELIVERY_SITE"
    ]


# Initialization of the list that will contain each row of the future table

output_list = []


# Iteration over contract notices

print('--- Processing ---')
for count, (i, row) in enumerate(award_notices.iterrows(), start=1):
    try:


# Extraction of the relevant parts of contract notices

        gestion = json.loads(row['gestion'])
        str_data = row['donnees']
        json_data = json.loads(str_data)
        identity = get_data_identity(json_data)
        json_procedure = get_data_procedure(json_data)
        award_data = get_data_award(json_data)
        object_data = get_data_object(json_data)
        previous_data = get_previous_data(json_data)


# Identification of the common information for all the potential lots of the contract

        idBOAMP_call = get_call_id(gestion)
        common_data = {
            "ID_BOAMP_AWARD": row['idweb'],
            "ID_BOAMP_CONTRACT": idBOAMP_call,
            "AWARD_NOTICE_DATE": row['dateparution'],
            "CONTRACT_NOTICE_DATE": '',
            "AWARD_DATE": '',
            "ID_LOT": '',
            "THRESHOLD": row['famille'],
            "OBJECT": row['objet'],
            "CAE_STATED_NAME": row['nomacheteur'],
            "CAE_SIRET": get_cae_siret(identity),
            "CAE_ADDRESS": get_cae_address(identity),
            "CAE_TOWN": get_cae_town(identity),
            "CAE_ZIP_CODE": get_cae_zip(identity),
            "WIN_STATED_NAME": '',
            "WIN_SIRET": '',
            "WIN_ADDRESS": '',
            "WIN_TOWN": '',
            "WIN_ZIP_CODE": '',
            "WIN_COUNTRY_CODE": '',
            "CORRECTIONS": get_number_corrections(gestion),
            "OUTCOME": '',
            "RENEWABLE": '',
            "DURATION": '',
            "RESERVED_CONTRACT": '',
            "EXECUTION_NUTS": '',
            "EXECUTION_SITE": '',
            "DELIVERY_SITE": get_delivery_site(object_data),
            "ESTIMATED_PRICE": '',
            "AWARD_PRICE": '',
            "MIN_OFFER": '',
            "MAX_OFFER": '',
            "CPV": '',
            "NUMBER_OFFERS": '',
            "ON_BEHALF": get_on_behalf(identity),
            "CENTRAL_PROCUREMENT": get_central_procurement(identity),
            "FRAMEWORK_AGREEMENT": get_framework_agreement(str_data),
            "NUMBER_LOTS": '',
            "ACCELERATED": get_accelerated_procedure(json_procedure),
            "CONTRACTOR_SME": '',
            "NUMBER_OFFERS_SME": '',
            "SUBCONTRACTING": '',
            "AGP": get_AGP(str_data),
            "BUSINESS_ASSOCIATION": '',
            "CONTRACT_TYPE": row['type_marche'],
            "PROCEDURE_TYPE": row['procedure_libelle'],
            "Q_CRITERIA_TEXT": '',
            "Q_CRITERIA_WEIGHTS": '',
            "P_CRITERION_WEIGHT": '',
            "ENVIRONMENTAL_CLAUSE": get_environmental_clause(row['criteres']),
            "SOCIAL_CLAUSE": get_social_clause(row['criteres']),
            "CAE_STATED_TYPE": get_cae_category(get_data_category(json_data)),
            "CAE_STATED_ACTIVITY": get_cae_activity(get_main_activity(json_data)),
            "ADVERTISING": '',
            "EU_FUNDS": '',
            "NUMBER_EU_OFFERS": '',
            "NUMBER_NON_EU_OFFERS": '',
            'CAE_SIRET_KNOWN': '',
            'WIN_SIRET_KNOWN': '',
            'MULTI_WIN': ''
            }
        common_data['CAE_SIRET_KNOWN'] = bool(common_data['CAE_SIRET'])


# Looking for the CPV

        if 'CPV' in object_data:
            CPV = get_CPV(object_data['CPV'])
            common_data['CPV'] = CPV


# Looking for the corresponding contract notice

        if idBOAMP_call != '':
            if idBOAMP_call in contract_notices.index:
                call_date = contract_notices['dateparution'][idBOAMP_call]
                common_data['CONTRACT_NOTICE_DATE'] = call_date
                str_call_data = contract_notices['donnees'][idBOAMP_call]
                call_data = json.loads(str_call_data)


# Looking for the mension of a contract reserved for ESS companies :
    
                common_data['RESERVED_CONTRACT'] = type_reserved_contract(str_call_data)

# Looking for information in the contract notice to fill potential missing data in the award notice

                list_call_dictionary = []
                if 'OBJET' in call_data:
                    criteria_presence = criteria_presence_detection(str_call_data)
                    if 'LIEU_EXEC_LIVR' in call_data['OBJET'] and common_data['DELIVERY_SITE'] == '':
                        common_data['DELIVERY_SITE'] = get_delivery_site(call_data['OBJET'])
                    if 'TYPE_POUVOIR_ADJUDICATEUR' in call_data and common_data['CAE_STATED_TYPE'] == '':
                        common_data['CAE_STATED_TYPE'] = get_cae_category(call_data['TYPE_POUVOIR_ADJUDICATEUR'])
                    if 'ACTIVITE_PRINCIPALE' in call_data and common_data['CAE_STATED_ACTIVITY'] == '':
                        common_data['CAE_STATED_ACTIVITY'] = get_cae_activity(call_data['ACTIVITE_PRINCIPALE'])
                    if common_data['CPV'] == '' and 'CPV_OBJ' in call_data['OBJET']:
                        common_data['CPV'] = call_data['OBJET']['CPV_OBJ']
                    if 'LOTS' in call_data['OBJET']:
                        structured_lot = call_data['OBJET']['LOTS']['LOT']
                        if type(structured_lot) == dict:
                            list_call_dictionary.append(object_analysis(structured_lot, criteria_presence))
                        elif type(structured_lot) == list:
                            for lot in structured_lot:
                                list_call_dictionary.append(object_analysis(lot, criteria_presence))
                    else:
                        list_call_dictionary.append(object_analysis(call_data['OBJET'], criteria_presence))
                if 'IDENTITE' in call_data:
                    if common_data['CAE_STATED_NAME'] == '' and 'DENOMINATION' in call_data['IDENTITE']:
                        common_data['CAE_STATED_NAME'] = call_data['IDENTITE']['DENOMINATION']
                    if common_data['CAE_SIRET'] == '' and 'CODE_IDENT_NATIONAL' in call_data['IDENTITE']:
                        common_data['CAE_SIRET'] = call_data['IDENTITE']['CODE_IDENT_NATIONAL']
                    if common_data['CAE_ADDRESS'] == '' and 'ADRESSE' in call_data['IDENTITE']:
                        common_data['CAE_ADDRESS'] = call_data['IDENTITE']['ADRESSE']
                    if common_data['CAE_TOWN'] == '' and 'VILLE' in call_data['IDENTITE']:
                        common_data['CAE_TOWN'] = call_data['IDENTITE']['VILLE']
                    if common_data['CAE_ZIP_CODE'] == '' and 'CP' in call_data['IDENTITE']:
                        common_data['CAE_ZIP_CODE'] = call_data['IDENTITE']['CP']
                    if common_data['ON_BEHALF'] == '':
                        if 'AGIT_POUR_AUTRE_COMPTE_OUI' in call_data['IDENTITE']:
                            common_data['ON_BEHALF'] = True
                        elif 'AGIT_POUR_AUTRE_COMPTE_NON' in call_data['IDENTITE']:
                            common_data['ON_BEHALF'] = False
                    if common_data['CENTRAL_PROCUREMENT'] == '':
                        if 'ORGANISME_ACHETEUR_CENTRAL_OUI' in call_data['IDENTITE']:
                            common_data['CENTRAL_PROCUREMENT'] = True
                        elif 'ORGANISME_ACHETEUR_CENTRAL_NON' in call_data['IDENTITE']:
                            common_data['CENTRAL_PROCUREMENT'] = False
                    if common_data['FRAMEWORK_AGREEMENT'] == '':
                        common_data['FRAMEWORK_AGREEMENT'] = get_framework_agreement(str_call_data)
                common_data['ADVERTISING'] = get_advertising_duration(call_date, call_data)


# Assessement if the award criteria can't be found in the contract notice

        criteria_presence = criteria_presence_detection(str_data)


# Assessement if we may find lots in the contract

        if '"DIV_EN_LOTS": {"NON"' in str_data:
            common_data['NUMBER_LOTS'] = 1
        else:
            number_lots = ''
            list_id_lots = []


# Extracting the features of the lot's description

        list_object_dictionaries = []
        single_object = False
        if 'LOTS' in object_data:
            structured_lot = object_data['LOTS']['LOT']
            if type(structured_lot) == dict:
                list_object_dictionaries.append(lot_object_analysis(structured_lot, criteria_presence))
                number_lots = 1
            elif type(structured_lot) == list:
                for lot in structured_lot:
                    list_object_dictionaries.append(lot_object_analysis(lot, criteria_presence))
        else:
            list_object_dictionaries.append(lot_object_analysis(object_data, criteria_presence))
            single_object = True


# Extracting the features of the lot's award decision

        list_award_dictionaries = []
        if 'DECISION' in award_data:
            not_awarded = False
            decision = award_data['DECISION']
            if type(decision) == dict:
                if 'NUM_LOT' not in decision:
                    decision['NUM_LOT'] = 'XXX'
                lot_award_dictionary = lot_award_analysis(decision)
                if 'TITULAIRE' in decision and type(decision['TITULAIRE']) == dict:
                    winner_data = winner_analysis(decision['TITULAIRE'], False)
                    list_award_dictionaries.append(merge(lot_award_dictionary, winner_data))
                elif 'TITULAIRE' in decision and type(decision['TITULAIRE']) == list:
                    for winner in decision['TITULAIRE']:
                        winner_data = winner_analysis(winner, True)
                        list_award_dictionaries.append(merge(lot_award_dictionary, winner_data))
                else:
                    list_award_dictionaries.append(lot_award_dictionary)
            elif type(decision) == list:
                pseudo_count = 0
                for lot in decision:
                    pseudo_count += 1
                    if 'NUM_LOT' not in lot:
                        lot['NUM_LOT'] = str(pseudo_count)
                    lot_award_dictionary = lot_award_analysis(lot)
                    if 'TITULAIRE' in lot and type(lot['TITULAIRE']) == dict:
                        winner_data = winner_analysis(lot['TITULAIRE'], False)
                        list_award_dictionaries.append(merge(lot_award_dictionary, winner_data))
                    elif 'TITULAIRE' in lot and type(lot['TITULAIRE']) == list:
                        for winner in lot['TITULAIRE']:
                            winner_data = winner_analysis(winner, True)
                            list_award_dictionaries.append(merge(lot_award_dictionary, winner_data))
                    else:
                        list_award_dictionaries.append(lot_award_dictionary)
        else:
            if 'TOTALEMENT_INFRUCTUEUX' in award_data or 'SANS_SUITE' in award_data:
                not_awarded = True
                if 'TOTALEMENT_INFRUCTUEUX' in award_data:
                    outcome = 'unsuccessful'
                else:
                    outcome = 'cancelled'
                list_award_dictionaries = list_object_dictionaries
                for lot in list_award_dictionaries:
                    lot['OUTCOME'] = outcome
                    if 'ID_LOT' not in lot:
                        lot['ID_LOT'] = 'XXX'


# Exporting description towards award decisions

        if not not_awarded:
            for lot_object in list_object_dictionaries:
                if not lot_object is None and 'ID_LOT' in lot_object:
                    trouvé = False
                    for decision in list_award_dictionaries:
                        if decision['ID_LOT'] == lot_object['ID_LOT']:
                            for key in lot_object:
                                decision[key] = lot_object[key]
                            trouvé = True
                    if not trouvé:
                        for decision in list_award_dictionaries:
                            if comparing_titles(lot_object, decision):
                                for key in lot_object:
                                    decision[key] = lot_object[key]
                                trouvé = True
                    if not trouvé:
                        lot_object['OUTCOME'] = 'not_found'
                        list_award_dictionaries.append(lot_object)
                elif number_lots == 1 or single_object:
                    for decision in list_award_dictionaries:
                        for key in lot_object:
                            decision[key] = lot_object[key]


# Exporting des données antérieures vers l'attribution

        if idBOAMP_call != '':
            for call_lot in list_call_dictionary:
                if 'ID_LOT' in call_lot:
                    for decision in list_award_dictionaries:
                        if decision['ID_LOT'] == call_lot['ID_LOT']:
                            for key in call_lot:
                                if key not in decision and key != 'Q_CRITERIA_TEXT':
                                    decision[key] = call_lot[key]
                            if 'Q_CRITERIA_TEXT' not in decision and 'Q_CRITERIA_TEXT' in call_lot and 'P_CRITERION_WEIGHT' in call_lot:
                                decision['Q_CRITERIA_TEXT'] = call_lot['Q_CRITERIA_TEXT']
                                decision['P_CRITERION_WEIGHT'] = call_lot['P_CRITERION_WEIGHT']
                                decision['Q_CRITERIA_WEIGHTS'] = call_lot['Q_CRITERIA_WEIGHTS']
                elif number_lots == 1 or single_object:
                    for decision in list_award_dictionaries:
                        for key in call_lot:
                            if key not in decision and key != 'Q_CRITERIA_TEXT':
                                decision[key] = call_lot[key]
                        if 'Q_CRITERIA_TEXT' not in decision and 'Q_CRITERIA_TEXT' in call_lot and 'P_CRITERION_WEIGHT' in call_lot:
                                decision['Q_CRITERIA_TEXT'] = call_lot['Q_CRITERIA_TEXT']
                                decision['P_CRITERION_WEIGHT'] = call_lot['P_CRITERION_WEIGHT']
                                decision['Q_CRITERIA_WEIGHTS'] = call_lot['Q_CRITERIA_WEIGHTS']


# Trying to find award criteria in the procedure part of the award notice

        for decision in list_award_dictionaries:
            if 'Q_CRITERIA_TEXT' not in decision:
                common_data['Q_CRITERIA_TEXT'] = listing_procedure_criteria(json_procedure)[0]
                break
        for decision in list_award_dictionaries:
            if 'Q_CRITERIA_WEIGHTS' not in decision:
                common_data['Q_CRITERIA_WEIGHTS'] = listing_procedure_criteria(json_procedure)[1]
                break
        for decision in list_award_dictionaries:
            if 'P_CRITERION_WEIGHT' not in decision:
                common_data['P_CRITERION_WEIGHT'] = listing_procedure_criteria(json_procedure)[2]
                break


# Trying to find award criteria in the procedure part of the contract notice

        if idBOAMP_call != '' and idBOAMP_call in contract_notices.index and 'PROCEDURE' in call_data:
            correction = False
            success_procedure_contract = False
            if common_data['Q_CRITERIA_TEXT'] == '':
                for decision in list_award_dictionaries:
                    if 'P_CRITERION_WEIGHT' in decision:
                        if decision['P_CRITERION_WEIGHT'] == 100 and listing_procedure_criteria(call_data['PROCEDURE'])[0] != '':
                            common_data['Q_CRITERIA_TEXT'] = listing_procedure_criteria(call_data['PROCEDURE'])[0]
                            common_data['Q_CRITERIA_WEIGHTS'] = listing_procedure_criteria(call_data['PROCEDURE'])[1]
                            common_data['P_CRITERION_WEIGHT'] = listing_procedure_criteria(call_data['PROCEDURE'])[2]
                            correction = True
                            if common_data['Q_CRITERIA_WEIGHTS'] != '':
                                success_procedure_contract = True
                            break
            if not correction or not success_procedure_contract:
                if common_data['Q_CRITERIA_TEXT'] == '':
                    common_data['Q_CRITERIA_TEXT'] = listing_procedure_criteria(call_data['PROCEDURE'])[0]
                if common_data['Q_CRITERIA_WEIGHTS'] == '':
                    common_data['Q_CRITERIA_WEIGHTS'] = listing_procedure_criteria(call_data['PROCEDURE'])[1]
                if common_data['P_CRITERION_WEIGHT'] == '':
                    common_data['P_CRITERION_WEIGHT'] = listing_procedure_criteria(call_data['PROCEDURE'])[2]


# Assessement of the number of lots

        if common_data['NUMBER_LOTS'] != 1:
            for key in list_award_dictionaries:
                list_id_lots.append(key['ID_LOT'])
            number_lots = len(set(list_id_lots))
        common_data['NUMBER_LOTS'] = number_lots


# Deletion of lot identifiers

        keys_to_remove = ['DESCRIPTION', 'INTITULE']
        for decision in list_award_dictionaries:
            for key in keys_to_remove:
                decision.pop(key, None)


# Incorporation of the information common to all the contract

        for decision in list_award_dictionaries:
            for key in common_data:
                if key not in decision:
                    decision[key] = common_data[key]
            if common_data['P_CRITERION_WEIGHT'] not in ('', 100) and decision['P_CRITERION_WEIGHT'] in ('', 100):
                decision['P_CRITERION_WEIGHT'] = common_data['P_CRITERION_WEIGHT']
                decision['Q_CRITERIA_WEIGHTS'] = common_data['Q_CRITERIA_WEIGHTS']
            if common_data['Q_CRITERIA_TEXT'] != '' and decision['P_CRITERION_WEIGHT'] == 100:
                decision['P_CRITERION_WEIGHT'] = ''
                decision['Q_CRITERIA_WEIGHTS'] = ''
            output_list.append(decision)
    except:
        pass


# Releasing memory

del award_notices
del contract_notices


# Converting the list into a dataframe

table = pd.DataFrame(output_list, columns=variables)


# Categorization of the qualitative award criteria

table['Q_CRITERIA_TYPE'] = table['Q_CRITERIA_TEXT'].apply(apply_find_criterion_type)


# Deleting the weights of criteria when they do not make sense

table.loc[(table['Q_CRITERIA_WEIGHTS'] == 0) & (table['P_CRITERION_WEIGHT'] == 100) & (table['Q_CRITERIA_TEXT'] != ''), ['P_CRITERION_WEIGHT', 'Q_CRITERIA_WEIGHTS']] = ''


# Converting blank spaces into missing values

table = table.replace('', np.nan)


# Checking if we know the national identifiers of the awarded companies

table['WIN_SIRET_KNOWN'] = table['WIN_SIRET'].notna()


# Checking for multi award decisions that were split

table.loc[(((table['MULTI_WIN'] == False) | (table['BUSINESS_ASSOCIATION'] == False)) & table.duplicated(subset=['ID_BOAMP_AWARD', 'ID_LOT'])), 'MULTI_WIN'] = True
mask = table.apply(compare_lengths, axis=1)
table['P_CRITERION_WEIGHT'] = table['P_CRITERION_WEIGHT'].astype(object)
table['Q_CRITERIA_WEIGHTS'] = table['Q_CRITERIA_WEIGHTS'].astype(object)
table.loc[mask, ['P_CRITERION_WEIGHT', 'Q_CRITERIA_WEIGHTS']] = ''


# Conversion of dates to a date format

table['CONTRACT_NOTICE_DATE'] = pd.to_datetime(table['CONTRACT_NOTICE_DATE'], errors='coerce')
table['AWARD_DATE'] = pd.to_datetime(table['AWARD_DATE'], errors='coerce')


# Gathering variables on the execution site (prioritizing the most accurate level of information)

table['EXECUTION_SITE'] = table['EXECUTION_SITE'].fillna(table['DELIVERY_SITE']).fillna(table['EXECUTION_NUTS'])
table = table.drop(['EXECUTION_NUTS', 'DELIVERY_SITE'], axis=1)


# Translating the information on procedures and types of contracts

translation_procedures = {
    'Procédure Ouverte': 'open',
    'Procédure Négociée': 'negotiated',
    'Procédure NC': 'no competition',
    'Procédure Dialogue compétitif': 'competitive dialogue',
    'Procédure Restreinte': 'restricted',
    'Procédure Concours restreint': 'restricted design contest',
    'Procédure Concours ouvert': 'open design contest',
    'Procédure Adaptée': 'adapted',
    'Procédure Partenariat innovation': 'innovation partnership'
}

table['PROCEDURE_TYPE'] = table['PROCEDURE_TYPE'].replace(translation_procedures)
table['CONTRACT_TYPE'] = table['CONTRACT_TYPE'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else x)
table['CONTRACT_TYPE'] = table['CONTRACT_TYPE'].apply(translate_types)


# Exporting the processed dataset

print('--- Exporting the processed table ---')

with open('processed_table.pkl', 'wb') as f:
    pickle.dump(table, f)

print('--- Completed ---')
