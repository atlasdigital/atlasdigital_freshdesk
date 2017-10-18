import requests
import json

def get_api_url(domain):
    api_url = "https://" + str(domain) + ".freshdesk.com/api/v2/"
    return api_url

def get_ticket_url(api_url, ticket_id):
    ticket_url = str(api_url) + "tickets/" + str(ticket_id)
    return ticket_url

def get_tickets_url_by_email_cmpny(api_url, customer_email, company):
    tickets_url = str(api_url) + "tickets?email=" + str(customer_email) \
    + "&company_id=" + str(company)
    return tickets_url

def get_tickets(user_email, pswd, tickets_url, headers):
    tickets_found = {}
    #curl -u eric@***REMOVED***:***REMOVED*** -H "Content-Type: application/json" -X GET \
    # 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets?email=cdixon@***REMOVED***&company_id=5000236189'
    rjson = requests.get(tickets_url, auth=(user_email, pswd), headers=headers)
    for tickets in rjson.json():
        ticket_found = {}
        ticket_found['group_id'] = tickets['group_id']
        ticket_found['type'] = tickets['type']
        ticket_found['description_text'] = tickets['description_text']
        tickets_found[tickets['id']] = ticket_found
    return tickets_found

def get_ticket_types_by_label(api_url, user_email, pswd, headers, label):
    rjson = requests.get(api_url+"ticket_fields", auth=(user_email, pswd), headers=headers)
    for fields in rjson.json():
        if fields['label'] == label:
            return fields['choices']

def ask_for_ticket_type_num(ticket_id, ticket_desc_text, ticket_types):
    print "\nTicket " + str(ticket_id), \
        " does not have a Type set, type the number of which", \
        "Type you want (Type 0 for Ticket description)"
    num = 1
    for ticket_type in ticket_types:
        print "  ("+str(num)+"): " + ticket_type
        num += 1
    ticket_type_num = input("Type: ")
    if ticket_type_num == 0:
        print ticket_desc_text
        ask_for_ticket_type_num(ticket_id, ticket_desc_text, ticket_types)
    return ticket_type_num

def update_company(
        user_email, pswd, ticket_id, temp_requester_id, requester_id, ticket_url, headers):
    #curl -u eric@***REMOVED***:***REMOVED*** -H "Content-Type: application/json" -X PUT -d \
    #'{"requester_id":12003568550}' 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets/10176'
    update_info = {
        'requester_id':temp_requester_id, 'type':'Technical Support', 'group_id':5000175231}
    rjson = requests.put(
        ticket_url, auth=(user_email, pswd), headers=headers, data=json.dumps(update_info))
    print user_email, pswd, ticket_id, temp_requester_id, requester_id, ticket_url, headers
    print rjson.text
    #curl -u eric@***REMOVED***:***REMOVED*** -H "Content-Type: application/json" -X PUT -d \
    # '{"requester_id":5007580195}' 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets/10176'
    #r = requests.put(ticket_url, auth=(user_email,pswd), headers=headers, \
    # data={"requester_id":"requester_id"})

def main():
    json_headers = {'Content-type': 'application/json'}
    # statics by variable or config
    domain = "atlasdigitalsupport"
    user = "eric@***REMOVED***"
    pswd = "***REMOVED***"
    temp_requester_id = 12003568550
    # to be provided
    requester_email = "cdixon@***REMOVED***"
    old_company_id = 5000236189
    new_company_id = ""
    # to be derived by email
    requester_id = 5007580195
    api_url = get_api_url(domain)
    tickets_url = get_tickets_url_by_email_cmpny(api_url, requester_email, old_company_id)
    #print(tickets_url)

    #todo: which fields are "required_for_agents": true
    ticket_ids = get_tickets(user, pswd, tickets_url, json_headers)

    for ticket_id in ticket_ids.iteritems():
        ticket_url = get_ticket_url(api_url, ticket_id[0])
        # If there's no Type set, get available types and ask user selection
        # Type of ticket  'Technical Support,Site Survey,Phone Support,Installation,Sales'
        if ticket_id[1]['type'] == "No Type Set":
            ticket_types = get_ticket_types_by_label(api_url, user, pswd, json_headers, "Type")
            ticket_type_num = ask_for_ticket_type_num(
                ticket_id[0], ticket_id[1]['description_text'], ticket_types)
            ticket_type = ticket_types[ticket_type_num-1]
            print ticket_type

        '''todo: type of group:
        PilotWare Support = 12000000933, 
        Technical Support = 5000175231, 
        Sales = 5000188665
        '''
        #if ticket_id[1]['default_group'] == "No Type Set":
        update_company(
            user, pswd, ticket_id, temp_requester_id, requester_id, ticket_url, json_headers)
        exit()
if __name__ == "__main__":
    main()
