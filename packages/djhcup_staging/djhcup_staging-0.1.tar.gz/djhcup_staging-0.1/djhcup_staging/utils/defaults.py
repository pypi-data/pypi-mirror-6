import os, re

def DataSource_select_or_add(source_dict):
    result = False
    
    from djhcup_staging.models import DataSource
    qs = DataSource.objects.filter(**source_dict)
    
    if qs.count() == 1:
        result = qs[0]
    elif qs.count() == 0:
        result = DataSource(**source_dict)
        result.save()
    
    return result


def FileType_select_or_add(ft_dict):
    result = False
    
    from djhcup_staging.models import FileType
    qs = FileType.objects.filter(**ft_dict)
    if qs.count() == 1:
        result = qs[0]
    elif qs.count() == 0:
        result = FileType(**ft_dict)
        result.save()
    
    return result


def populate_hcup():
    #these are up top for config/maintenance
    template_pattern = '(?P<state_abbr>[A-Z]{2})_<<file>>_(?P<year>[0-9]{4})_<<category>>\.(?P<file_extension><<file_extension>>)'
    hcup_master = {'name': 'Healthcare Cost and Utilization Project', 'abbreviation': 'HCUP'}
    hcup_files = [{'name': 'State Inpatient Database', 'abbreviation': 'SID', 'patterns': ['SID', 'SIDC']},
                  {'name': 'State Emergency Department Database', 'abbreviation': 'SEDD'},
                  {'name': 'State Ambulatory Surgery Database', 'abbreviation': 'SASD'},
                  ]
    hcup_categories = [{'name': 'Core discharge data', 'abbreviation': 'CORE'},
                    {'name': 'Charges data', 'abbreviation': 'CHGS'},
                    {'name': 'Severity data', 'abbreviation': 'SEVERITY'},
                    {'name': 'Diagnosis/procedure CCS data', 'abbreviation': 'DX_PR_GRPS'},
                    {'name': 'American Hospital Association linkage data', 'abbreviation': 'AHAL'},
                    ]
    file_types = [{'patterns': ['exe', 'zip'], 'content': 'CONTENTNH', 'compression': 'ZIP'},
                {'patterns': ['asc'], 'content': 'CONTENTNH', 'compression': 'NONE'},
                {'patterns': ['sas'], 'content': 'LOAD', 'compression': 'NONE'},
                ]
    
    p_or_abbr = lambda x: x['abbreviation'] if 'patterns' not in x else '|'.join(x['patterns'])
    
    #get going with the actual work
    hcup_source = DataSource_select_or_add(hcup_master)
    
    if hcup_source is False:
        #can't select or add, usually due to multiple records matching passed dictionary
        raise Exception("Unable to add or select top-level HCUP source; this is usually due to multiple pre-existing DataSource records, preventing unambiguous selection of existing DataSource record representing HCUP")
    else:
        #proceed
        for f in hcup_files:
            #select or add file DataSource and replace relevant pattern chunk
            f_dict = {'name': f['name'],
                      'abbreviation': f['abbreviation'],
                      'parent': hcup_source,
                     }
            f_source = DataSource_select_or_add(f_dict)
            f_pattern = template_pattern.replace('<<file>>', '(%s)' % p_or_abbr(f))
            
            for c in hcup_categories:
                c_dict = {'name': c['name'],
                          'abbreviation': c['abbreviation'],
                          'parent': f_source,
                          }
                #select or add category DataSource and replace relevant pattern chunk
                c_source = DataSource_select_or_add(c_dict)
                cat_pattern = f_pattern.replace('<<category>>', '(%s)' % p_or_abbr(c))
                #cat_name = 'HCUP %s %s' % (f['abbreviation'], c['abbreviation'])
                
                for ftype in file_types:
                    ftype['abbreviation'] = ftype['content']
                    ftype_pattern = cat_pattern.replace('<<file_extension>>', '(%s)' % p_or_abbr(ftype))
                    ft_dict = {'source': c_source,
                               'pattern': ftype_pattern,
                               'content_type': ftype['content'],
                               'compression': ftype['compression']
                               }
                    ft = FileType_select_or_add(ft_dict)


def populate_pudf():
    #these are up top for config/maintenance
    pudf_master = {'name': 'Texas Inpatient Public Use Data File', 'abbreviation': 'PUDF'}
    pudf_categories = [{'name': 'Core discharge data', 'abbreviation': 'base'},
                       {'name': 'Charges data', 'abbreviation': 'charges'},
                       {'name': 'Facility-level data', 'abbreviation': 'facility'}
                       ]
    
    #only looks for inflated (non-zipped) content
    file_type = {'content': 'CONTENTNH', 'compression': 'NONE'}
    
    # NB 1999-2003 all were category='base'
    tx1999_2003_template = '(?:pudf|PUDF)(?P<quarter>[1-4]{1})(q|Q)(?P<year>99|200[0-3])\.(?P<file_extension>txt)'
    tx2004_2010_template = '(?:PUDF)_<<category>>(?P<quarter>[1-4]{1})(q|Q)(?P<year>2010|200[4-9])\.(?P<file_extension>txt)'
    
    pattern_templates = [{'base_only': True, 'p': tx1999_2003_template},
                         {'base_only': False, 'p': tx2004_2010_template}
                         ]
    
    tx_loadfile_template = 'tx_pudf_(?P<year>\d{4})_<<category>>_definition\.(?P<file_extension>txt)'
    
    p_or_abbr = lambda x: x['abbreviation'] if 'patterns' not in x else '|'.join(x['patterns'])
    
    #get going with the actual work
    pudf_source = DataSource_select_or_add(pudf_master)
    
    if pudf_source is False:
        #can't select or add, usually due to multiple records matching passed dictionary
        raise Exception("Unable to add or select top-level PUDF source; this is usually due to multiple pre-existing DataSource records, preventing unambiguous selection of existing DataSource record representing PUDF")
    else:
        for pt in pattern_templates:
            for c in pudf_categories:
                c_dict = {'name': c['name'],
                          'abbreviation': c['abbreviation'],
                          'parent': pudf_source,
                          }
                c_source = DataSource_select_or_add(c_dict)
                
                # 1999-2003 only has category=base
                if pt['base_only'] == True:
                    if c_source.abbreviation == 'base':
                        ft_dict = {'source': c_source,
                                   'pattern': pt['p'],
                                   'content_type': file_type['content'],
                                   'compression': file_type['compression']
                                   }
                        ft = FileType_select_or_add(ft_dict)
                        lft_dict = {'source': c_source,
                                    'pattern': tx_loadfile_template.replace('<<category>>', '(base)'),
                                    'content_type': 'LOAD',
                                    'compression': 'NONE'
                                    }
                        lft = FileType_select_or_add(lft_dict)
                
                else:
                    # 2004-2010 have both category=base and category=charges
                    cat_pattern = pt['p'].replace('<<category>>', '(%s)' % p_or_abbr(c))
                    ft_dict = {'source': c_source,
                               'pattern': cat_pattern,
                               'content_type': file_type['content'],
                               'compression': file_type['compression']
                               }
                    ft = FileType_select_or_add(ft_dict)
                    lft_dict = {'source': c_source,
                                'pattern': tx_loadfile_template.replace('<<category>>', '(%s)' % p_or_abbr(c)),
                                'content_type': 'LOAD',
                                'compression': 'NONE'
                                }
                    lft = FileType_select_or_add(lft_dict)
