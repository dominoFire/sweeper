from gcloud import datastore


if __name__ == '__main__':
    datastore_client = datastore.Client.from_service_account_json(
        json_credentials_path='data/pulsarcloud-sweeper.json',
        project='ml-pulsarcloud')
    qry = datastore.Query(kind='ResourceConfiguration', client=datastore_client)

    for result in qry.fetch():
        print(result)

    qry_filter = datastore.Query(kind='ResourceConfiguration', client=datastore_client)
    qry_filter.add_filter('config_name', '=', 'A1')

    print(type(qry_filter))
    for result in qry_filter.fetch():
        print(result)
