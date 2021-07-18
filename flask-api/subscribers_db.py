import pymongo
mongoclient = pymongo.MongoClient("mongodb://localhost:27018/")
db=mongoclient['free5gc']
authSubsDataColl = db["subscriptionData.authenticationData.authenticationSubscription"]
amDataColl       = db["subscriptionData.provisionedData.amData"]
smDataColl       = db["subscriptionData.provisionedData.smData"]
smfSelDataColl   = db["subscriptionData.provisionedData.smfSelectionSubscriptionData"]
amPolicyDataColl = db["policyData.ues.amData"]
smPolicyDataColl = db["policyData.ues.smData"]
flowRuleDataColl = db["policyData.ues.flowRule"]
list_of_colls_to_be_updated=[authSubsDataColl,amDataColl,smDataColl,smfSelDataColl,amPolicyDataColl,smPolicyDataColl]

def insert_subscriber(data):
    for coll in list_of_colls_to_be_updated:
        insert_into_coll(data,coll)
    return
def delete_subscriber(data):
    for coll in list_of_colls_to_be_updated:
        coll.find_one_and_delete({'ueId':data['ueId']})
    return
def modify_subscriber(data,updated_data):
    for coll in list_of_colls_to_be_updated:
        coll.find_one_and_update({'ueId':data['ueId']},{"$set":{'ueId':updated_data['ueId']}})
    return
def view_subscribers():
    list_of_imsis=authSubsDataColl.find({},{'ueId': 1,'_id':0})
    output={}
    for i,imsi in enumerate(list_of_imsis):
        output[i]=imsi
    return output

def insert_into_coll(data_dict,coll):
    check=coll.find({"ueId":data_dict["ueId"]})
    outs=list(check)
    print (outs)
    if len(outs)==0:
        auth_temp=coll.find_one()
        del auth_temp["_id"]
        auth_temp['ueId'] = data_dict['ueId']
        coll.insert_one(auth_temp)
    return



