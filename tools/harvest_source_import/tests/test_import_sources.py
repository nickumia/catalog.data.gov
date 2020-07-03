import pytest
from remote_ckan.lib import RemoteCKAN


@pytest.mark.vcr()
def test_load_from_url():
    """ Test with some previous harvester already saved
        Use a pytest cassette so real requests are not required. 
        We import 3 harvest sources (so they already exists) 
        and then run this test with 6 sources. """

    ckan = RemoteCKAN(url='https://catalog.data.gov')
    ckan.set_destination(ckan_url='http://ckan:5000',
                         ckan_api_key='783b1397-3a9f-4ffe-81c3-c67cc85ef5f1')

    print('Getting harvest sources ...')
    names = ['fdic-data-json', 'fcc', 'doi-cas-datajam', 'fhfa-json']
    hss = [{'name': name} for name in names]
    for hs in hss:  # ckan.list_harvest_sources(source_type='datajson', limit=3):
        name = hs['name']
        full_hs = ckan.get_full_harvest_source(hs={'name': name})
        ckan.create_harvest_source(data=full_hs)
        assert 'created' in ckan.harvest_sources[hs['name']].keys()
        assert 'updated' in ckan.harvest_sources[hs['name']].keys()
        assert 'error' in ckan.harvest_sources[hs['name']].keys()

    created = len([k for k, v in ckan.harvest_sources.items() if v['created'] ])
    updated = len([k for k, v in ckan.harvest_sources.items() if v['updated'] ])
    errors = len([k for k, v in ckan.harvest_sources.items() if v['error'] ])
    total = created + updated + errors

    # test organization extras
    extras = ckan.organizations['fdic-gov'].get('extras', [])
    expected_email_list = 'dmentall@fdic.gov\r\njemartinez@fdic.gov'
    assert expected_email_list in [extra['value'] for extra in extras if extra['key'] == 'email_list']

    extras = ckan.organizations['fcc-gov'].get('extras', [])
    expected_email_list = 'hyon.kim@gsa.gov\r\ncrystal.carter@gsa.gov'
    assert expected_email_list in [extra['value'] for extra in extras if extra['key'] == 'email_list']

    print('Finished: {} harvest sources. {} Added, {} already exists, {} failed'.format(total, created, updated, errors))

    assert total == len(ckan.harvest_sources)
    assert created == 1
    assert updated == 3
    assert errors == 0

