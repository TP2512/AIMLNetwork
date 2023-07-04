from InfrastructureSVG.ACP_Infrastructure.ACP_Infra import ACPInfra

if __name__ == "__main__":
    xxx = ACPInfra(acp_name="asil-svg-acp3")
    # xxx.delete_object("Site", "smorgon")
    # xxx.get_object("Site", "Auto Discovery Site")
    data = {
        # "bandwidthMhz": "100",
        "maxTxPower": 1,

    }
    data_keys = list(data.keys())
    data_values = list(data.values())

    # xxx.update_object("gnbru", "1EU213100016", user_data={"bandwidth": "100"})
    # list_of_ids = xxx.convert_list_of_names_to_ids(acp_object_name="Gnb", list_of_names=datax)
    # xxx.action_on_object(acp_object_name="Gnb", object_name="Toyota", action="reprovisionMulti", data=datax)
    # xxx.action_on_object(acp_object_name="Gnb", action="dissociateNetworkFunctions")
    # xxx.create_object(acp_object_name="GnbDiscoveryTask", data=data)
    xxx.update_object(acp_object_name="GnbDu", object_name="DU-airspan-1-1", user_data=data, path_to_fields="['duCellList'][0]")
    # xxx.get_object(acp_object="Gnb", object_name="Toyota")
