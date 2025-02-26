import logging
def validate_datastore(gis):
    logging.getLogger().setLevel(logging.ERROR)
    hosting_server = gis.admin.servers.get(role="HOSTING_SERVER")[0]    
    logging.getLogger().setLevel(logging.INFO)
    try:
        datastores = hosting_server.datastores.list()
    except TypeError as e:
        logging.error(f"Type error while listing datastores: {str(e)}")
        return

    for ds in datastores:
        if "/enterpriseDatabases/AGSDataStore" in ds.path:
            #logging.info(ds.path)
            datastore_name = ds.path.split('/')[-1]

            try:
                machine = ds.info['machines'][0]
            except (KeyError, IndexError) as e:
                logging.error(f"Missing machine info for datastore {ds.path}: {str(e)}")
                continue

            try:
                r_validation_output = hosting_server.datastores.validate_egdb(datastore_name, machine['name'])
            except ConnectionError as e:
                logging.error(f"Connection error while validating datastore {datastore_name}: {str(e)}")
                continue
            try:
                if 'datastore.isReadOnly' in r_validation_output :
                    r_modified_output = { 
                        "datastore.isReadOnly": r_validation_output['datastore.isReadOnly'],   
                        "machines": [
                            {
                                "machine.overallhealth": machine['machine.overallhealth'],
                                "machine.isReachable": machine['machine.isReachable'],
                                "name": machine['name'],
                                "role": machine['role'],
                                "status": machine['status'],
                                "db.isactive": machine['db.isactive'],
                                "db.isAccepting": machine['db.isAccepting'],
                                "db.isInRecovery": machine.get('db.isInRecovery') == "true"
                            }
                            for machine in r_validation_output.get('machines', [])
                        ],
                        "datastore.status": r_validation_output['datastore.status'],
                        "datastore.isActiveHA": r_validation_output['datastore.isActiveHA'],
                        "datastore.hasValidServerConnection": r_validation_output['datastore.hasValidServerConnection'],
                        "status": r_validation_output['status']
                    }
                else :
                    r_modified_output = { 
                        "machines": [
                            {
                                "machine.overallhealth": machine['machine.overallhealth'],
                                "machine.isReachable": machine['machine.isReachable'],
                                "name": machine['name'],
                                "role": machine['role'],
                                "status": machine['status'],
                                "db.isactive": machine['db.isactive'],
                                "db.isAccepting": machine['db.isAccepting'],
                                "db.isInRecovery": machine.get('db.isInRecovery') == "true"
                            }
                            for machine in r_validation_output.get('machines', [])
                        ],
                        "datastore.status": r_validation_output['datastore.status'],
                        "datastore.isActiveHA": r_validation_output['datastore.isActiveHA'],
                        "datastore.hasValidServerConnection": r_validation_output['datastore.hasValidServerConnection'],
                        "status": r_validation_output['status']
                    }
                #logging.info(r_modified_output)

                if r_validation_output['status'] == "success":
                    logging.info(f"Relational Datastore {ds.path} validation is successful")
            except KeyError as e:
                logging.error("Key Error occured")
                continue