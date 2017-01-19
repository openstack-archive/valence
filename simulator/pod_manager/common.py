import uuid


def generate_members(element_name, url, total_num):
    members = []
    i = 0
    while i < total_num:
        dic = dict()
        dic["@odata.id"] = url + element_name + str(i + 1)
        members.append(dic)
        i += 1
    return members


def generate_uuid_by_element_id(element_id):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, element_id))
